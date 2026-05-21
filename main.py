import taichi as ti

# 初始化 Taichi
ti.init(arch=ti.gpu)

# 窗口分辨率
res_x, res_y = 800, 600
pixels = ti.Vector.field(3, dtype=ti.f32, shape=(res_x, res_y))

# 定义全局交互参数
Ka = ti.field(ti.f32, shape=())
Kd = ti.field(ti.f32, shape=())
Ks = ti.field(ti.f32, shape=())
shininess = ti.field(ti.f32, shape=())

@ti.func
def normalize(v):
    return v / v.norm(1e-5)

# --- 几何体相交测试函数 ---

@ti.func
def intersect_sphere(ro, rd, center, radius):
    """测试光线与球体相交"""
    t = -1.0
    normal = ti.Vector([0.0, 0.0, 0.0])
    oc = ro - center
    b = 2.0 * oc.dot(rd)
    c = oc.dot(oc) - radius * radius
    delta = b * b - 4.0 * c
    if delta > 0:
        t1 = (-b - ti.sqrt(delta)) / 2.0
        if t1 > 0:
            t = t1
            p = ro + rd * t
            normal = normalize(p - center)
    return t, normal

@ti.func
def intersect_cone(ro, rd, apex, base_y, radius):
    """测试光线与竖直圆锥相交"""
    t = -1.0
    normal = ti.Vector([0.0, 0.0, 0.0])
    H = apex.y - base_y
    k = (radius / H) ** 2
    
    ro_local = ro - apex
    A = rd.x**2 + rd.z**2 - k * rd.y**2
    B = 2.0 * (ro_local.x * rd.x + ro_local.z * rd.z - k * ro_local.y * rd.y)
    C = ro_local.x**2 + ro_local.z**2 - k * ro_local.y**2
    
    if ti.abs(A) > 1e-5:
        delta = B**2 - 4.0 * A * C
        if delta > 0:
            t1 = (-B - ti.sqrt(delta)) / (2.0 * A)
            t2 = (-B + ti.sqrt(delta)) / (2.0 * A)
            
            t_first = t1
            t_second = t2
            if t1 > t2:
                t_first, t_second = t_second, t1
                
            y1 = ro_local.y + t_first * rd.y
            if t_first > 0 and -H <= y1 <= 0:
                t = t_first
            else:
                y2 = ro_local.y + t_second * rd.y
                if t_second > 0 and -H <= y2 <= 0:
                    t = t_second
                    
            if t > 0:
                p_local = ro_local + rd * t
                normal = normalize(ti.Vector([p_local.x, -k * p_local.y, p_local.z]))
                
    return t, normal

@ti.func
def check_shadow(ro, rd, light_dist):
    """
    暗影射线求交测试 (硬阴影)
    如果射线在到达光源前击中了任何物体，返回 True
    """
    in_shadow = False
    
    # 检查左侧红球
    t_sph, _ = intersect_sphere(ro, rd, ti.Vector([-1.2, -0.2, 0.0]), 1.2)
    if 0.0 < t_sph < light_dist:
        in_shadow = True
        
    # 检查右侧紫锥
    if not in_shadow:
        t_cone, _ = intersect_cone(ro, rd, ti.Vector([1.2, 1.2, 0.0]), -1.4, 1.2)
        if 0.0 < t_cone < light_dist:
            in_shadow = True
            
    return in_shadow

@ti.kernel
def render():
    for i, j in pixels:
        u = (i - res_x / 2.0) / res_y * 2.0
        v = (j - res_y / 2.0) / res_y * 2.0
        
        ro = ti.Vector([0.0, 0.0, 5.0])
        rd = normalize(ti.Vector([u, v, -1.0]))

        min_t = 1e10
        hit_normal = ti.Vector([0.0, 0.0, 0.0])
        hit_color = ti.Vector([0.0, 0.0, 0.0])
        
        # 1. 场景相交测试 (Z-Buffer 逻辑)
        t_sph, n_sph = intersect_sphere(ro, rd, ti.Vector([-1.2, -0.2, 0.0]), 1.2)
        if 0 < t_sph < min_t:
            min_t = t_sph
            hit_normal = n_sph
            hit_color = ti.Vector([0.8, 0.1, 0.1])
            
        t_cone, n_cone = intersect_cone(ro, rd, ti.Vector([1.2, 1.2, 0.0]), -1.4, 1.2)
        if 0 < t_cone < min_t:
            min_t = t_cone
            hit_normal = n_cone
            hit_color = ti.Vector([0.6, 0.2, 0.8])

        # 默认背景色
        color = ti.Vector([0.05, 0.15, 0.15]) 

        if min_t < 1e9:
            p = ro + rd * min_t
            N = hit_normal
            
            # 光源设置
            light_pos = ti.Vector([2.0, 3.0, 4.0])
            light_color = ti.Vector([1.0, 1.0, 1.0]) 
            
            # 计算光源方向向量、距离以及视线向量
            L_unnorm = light_pos - p
            light_dist = L_unnorm.norm(1e-5)
            L = normalize(L_unnorm)
            V = normalize(ro - p)

            # --- 选做功能：硬阴影 (Hard Shadow) ---
            # 引入 epsilon (1e-4) 稍微抬高射线起点，彻底避免自交引起的阴影粉刺 (Shadow Acne)
            shadow_ro = p + 1e-4 * N 
            is_occluded = check_shadow(shadow_ro, L, light_dist)
            
            # 基础环境光 (无论是否在阴影中都存在)
            ambient = Ka[None] * light_color * hit_color
            
            diffuse = ti.Vector([0.0, 0.0, 0.0])
            specular = ti.Vector([0.0, 0.0, 0.0])
            
            # 如果没有被遮挡，才计算漫反射与镜面高光
            if not is_occluded:
                # 漫反射
                diff = ti.max(0.0, N.dot(L))
                diffuse = Kd[None] * diff * light_color * hit_color
                
                # --- 选做功能：Blinn-Phong 光照模型 ---
                # 计算半程向量 H
                H = normalize(L + V)
                spec = ti.max(0.0, N.dot(H)) ** shininess[None]
                specular = Ks[None] * spec * light_color 
            
            color = ambient + diffuse + specular
                
        pixels[i, j] = ti.math.clamp(color, 0.0, 1.0)

def main():
    window = ti.ui.Window("Blinn-Phong & Hard Shadow Demo", (res_x, res_y))
    canvas = window.get_canvas()
    gui = window.get_gui()
    
    # 初始化材质参数
    Ka[None] = 0.2
    Kd[None] = 0.7
    Ks[None] = 0.5
    shininess[None] = 32.0

    while window.running:
        render()
        canvas.set_image(pixels)
        
        with gui.sub_window("Material Parameters", 0.7, 0.05, 0.28, 0.22):
            Ka[None] = gui.slider_float('Ka (Ambient)', Ka[None], 0.0, 1.0)
            Kd[None] = gui.slider_float('Kd (Diffuse)', Kd[None], 0.0, 1.0)
            Ks[None] = gui.slider_float('Ks (Specular)', Ks[None], 0.0, 1.0)
            shininess[None] = gui.slider_float('N (Shininess)', shininess[None], 1.0, 128.0)

        window.show()

if __name__ == '__main__':
    main()