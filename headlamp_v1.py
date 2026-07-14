import bpy, math

# ---------- 초기화 ----------
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

def mat(name, base=(0.8,0.8,0.8,1), metallic=0.0, rough=0.5,
        emission=None, e_str=0.0, transmission=0.0, ior=1.45, alpha=1.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = base
    b.inputs["Metallic"].default_value = metallic
    b.inputs["Roughness"].default_value = rough
    if "Transmission Weight" in b.inputs:
        b.inputs["Transmission Weight"].default_value = transmission
    b.inputs["IOR"].default_value = ior
    b.inputs["Alpha"].default_value = alpha
    if emission:
        b.inputs["Emission Color"].default_value = emission
        b.inputs["Emission Strength"].default_value = e_str
    return m

# 재질
m_housing = mat("Housing", (0.02,0.02,0.022,1), rough=0.35)          # 검정 하우징
m_bezel   = mat("Bezel",   (0.01,0.01,0.012,1), rough=0.15)          # 글로시 베젤
m_chrome  = mat("Chrome",  (0.9,0.9,0.92,1), metallic=1.0, rough=0.08)
m_body    = mat("Body",    (0.35,0.37,0.39,1), metallic=0.9, rough=0.35) # 차체 실버
m_glass   = mat("Lens",    (1,1,1,1), rough=0.02, transmission=1.0, ior=1.45)
m_glass.blend_method = 'BLEND'
m_proj   = mat("Projector",(0.6,0.7,0.8,1), rough=0.05, transmission=0.9, ior=1.6,
               emission=(0.75,0.85,1,1), e_str=3.0)
m_drl    = mat("DRL", (1,1,1,1), emission=(0.8,0.9,1,1), e_str=25.0)
m_ring   = mat("Ring",(1,1,1,1), emission=(0.85,0.92,1,1), e_str=15.0)

objs = []
def add(o, m):
    o.data.materials.append(m); objs.append(o); return o

# ---------- 차체 패널 (배경) ----------
bpy.ops.mesh.primitive_cube_add(location=(0, 0.35, 0))
body = bpy.context.object
body.scale = (2.6, 0.5, 1.1)
add(body, m_body)

# ---------- 헤드램프 하우징 (슬림 가로형) ----------
bpy.ops.mesh.primitive_cube_add(location=(0, -0.18, 0))
hs = bpy.context.object
hs.scale = (1.9, 0.35, 0.42)
mod = hs.modifiers.new("Bevel", 'BEVEL'); mod.width = 0.12; mod.segments = 6
add(hs, m_housing)

# 내부 베젤
bpy.ops.mesh.primitive_cube_add(location=(0, -0.30, 0))
bz = bpy.context.object
bz.scale = (1.75, 0.22, 0.33)
mod = bz.modifiers.new("Bevel", 'BEVEL'); mod.width = 0.08; mod.segments = 5
add(bz, m_bezel)

# ---------- 프로젝터 유닛 2개 ----------
for i, x in enumerate([-0.95, -0.15]):
    r = 0.26 if i == 0 else 0.22
    # 크롬 콘(리플렉터)
    bpy.ops.mesh.primitive_cone_add(vertices=48, radius1=r*1.25, radius2=r*0.6,
        depth=0.28, location=(x, -0.42, 0), rotation=(math.pi/2, 0, 0))
    add(bpy.context.object, m_chrome)
    # 프로젝터 렌즈 (반구)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24,
        radius=r, location=(x, -0.52, 0))
    lens = bpy.context.object
    lens.scale = (1, 0.55, 1)
    bpy.ops.object.shade_smooth()
    add(lens, m_proj)
    # 발광 링 (DRL 시그니처)
    bpy.ops.mesh.primitive_torus_add(major_radius=r*1.18, minor_radius=0.018,
        location=(x, -0.50, 0), rotation=(math.pi/2, 0, 0))
    add(bpy.context.object, m_ring)

# ---------- 수평 DRL 바 ----------
bpy.ops.mesh.primitive_cube_add(location=(0.95, -0.48, 0.02))
drl = bpy.context.object
drl.scale = (0.72, 0.03, 0.045)
mod = drl.modifiers.new("Bevel", 'BEVEL'); mod.width = 0.02; mod.segments = 4
add(drl, m_drl)

# 방향지시등 스트립 (하단, 앰버 오프 상태 - 어두운 오렌지 틴트)
m_amber = mat("Amber", (0.35,0.12,0.02,1), rough=0.2)
bpy.ops.mesh.primitive_cube_add(location=(0.95, -0.46, -0.20))
ind = bpy.context.object
ind.scale = (0.72, 0.02, 0.035)
add(ind, m_amber)

# ---------- 외부 클리어 렌즈 커버 ----------
bpy.ops.mesh.primitive_cube_add(location=(0, -0.52, 0))
cov = bpy.context.object
cov.scale = (1.88, 0.06, 0.41)
mod = cov.modifiers.new("Bevel", 'BEVEL'); mod.width = 0.1; mod.segments = 6
add(cov, m_glass)

# ---------- 조명 & 카메라 ----------
def light(loc, energy, size, rot=(0,0,0)):
    bpy.ops.object.light_add(type='AREA', location=loc, rotation=rot)
    L = bpy.context.object
    L.data.energy = energy; L.data.size = size
    return L

light((2.5, -3.5, 2.5), 600, 3, rot=(math.radians(55), 0, math.radians(35)))
light((-3, -2.5, 1.0), 250, 2.5, rot=(math.radians(70), 0, math.radians(-50)))
light((0, -1.5, 3.5), 150, 4, rot=(0,0,0))

world = bpy.data.worlds.new("World"); scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.008,0.009,0.012,1)

bpy.ops.object.camera_add(location=(2.4, -3.2, 0.9),
    rotation=(math.radians(78), 0, math.radians(37)))
cam = bpy.context.object
cam.data.lens = 60
scene.camera = cam

# ---------- 렌더 설정 ----------
scene.render.engine = 'CYCLES'
scene.cycles.samples = 32
scene.cycles.use_denoising = True
scene.cycles.device = 'CPU'
scene.render.resolution_x = 960
scene.render.resolution_y = 540
scene.render.filepath = "/home/claude/headlamp_render.png"
scene.render.image_settings.file_format = 'PNG'

bpy.ops.render.render(write_still=True)
print("DONE")
