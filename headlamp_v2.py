import bpy, math, random

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
random.seed(7)

def mat(name, base=(0.8,0.8,0.8,1), metallic=0.0, rough=0.5,
        emission=None, e_str=0.0, transmission=0.0, ior=1.45):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = base
    b.inputs["Metallic"].default_value = metallic
    b.inputs["Roughness"].default_value = rough
    if "Transmission Weight" in b.inputs:
        b.inputs["Transmission Weight"].default_value = transmission
    b.inputs["IOR"].default_value = ior
    if emission:
        b.inputs["Emission Color"].default_value = emission
        b.inputs["Emission Strength"].default_value = e_str
    return m

m_body    = mat("Body",   (0.05,0.28,0.30,1), metallic=0.85, rough=0.3)   # 브리티시 그린-틸 차체
m_housing = mat("Housing",(0.015,0.015,0.017,1), rough=0.4)
m_bezel   = mat("Bezel",  (0.008,0.008,0.01,1), rough=0.12)
m_chrome  = mat("Chrome", (0.92,0.92,0.94,1), metallic=1.0, rough=0.06)
m_dark_al = mat("DarkAlu",(0.25,0.26,0.28,1), metallic=1.0, rough=0.35)
m_glass   = mat("Glass",  (1,1,1,1), rough=0.015, transmission=1.0, ior=1.45)
m_glass.blend_method='BLEND'
m_projglass = mat("ProjGlass",(0.7,0.8,0.95,1), rough=0.03, transmission=0.95, ior=1.7,
                  emission=(0.7,0.82,1,1), e_str=1.5)
m_led   = mat("LED",  (1,1,1,1), emission=(0.75,0.87,1,1), e_str=40.0)
m_ring  = mat("Ring", (1,1,1,1), emission=(0.85,0.92,1,1), e_str=18.0)
m_amber = mat("Amber",(0.9,0.35,0.05,1), rough=0.15, transmission=0.6, ior=1.5,
              emission=(1,0.35,0.02,1), e_str=0.4)

def bevel(o, w=0.05, seg=5):
    md = o.modifiers.new("Bevel",'BEVEL'); md.width=w; md.segments=seg

def smooth(o):
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.shade_smooth()

def setmat(o, m): o.data.materials.append(m)

# ================= 차체 펜더 (곡면 배경) =================
bpy.ops.mesh.primitive_cube_add(location=(0, 0.55, -0.1))
body = bpy.context.object
body.scale=(3.2, 0.7, 1.5)
bevel(body, 0.45, 8)
sd = body.modifiers.new("Bend",'SIMPLE_DEFORM')
sd.deform_method='BEND'; sd.angle=math.radians(-25); sd.deform_axis='Z'
setmat(body, m_body); smooth(body)

# 보닛 캐릭터 라인
bpy.ops.mesh.primitive_cube_add(location=(0, 0.2, 0.62))
hood = bpy.context.object
hood.scale=(3.0, 0.55, 0.05)
bevel(hood, 0.04, 4)
setmat(hood, m_dark_al)

# ================= 헤드램프 하우징 (뒤로 감기는 형태) =================
bpy.ops.mesh.primitive_cube_add(location=(0, -0.15, 0))
hs = bpy.context.object
hs.scale=(2.0, 0.42, 0.46)
bevel(hs, 0.16, 8)
sd = hs.modifiers.new("Bend",'SIMPLE_DEFORM')
sd.deform_method='BEND'; sd.angle=math.radians(-32); sd.deform_axis='Z'
sd2 = hs.modifiers.new("Taper",'SIMPLE_DEFORM')
sd2.deform_method='TAPER'; sd2.factor=-0.35; sd2.deform_axis='X'
setmat(hs, m_housing); smooth(hs)

# 내부 계단식 베젤 3단
for i,(sx,sy,sz,y) in enumerate([(1.85,0.30,0.38,-0.26),(1.7,0.24,0.31,-0.33),(1.55,0.18,0.25,-0.39)]):
    bpy.ops.mesh.primitive_cube_add(location=(0.05*i, y, 0))
    b = bpy.context.object
    b.scale=(sx,sy,sz)
    bevel(b, 0.06, 5)
    sd = b.modifiers.new("Bend",'SIMPLE_DEFORM')
    sd.deform_method='BEND'; sd.angle=math.radians(-30); sd.deform_axis='Z'
    setmat(b, m_bezel); smooth(b)

# ================= 메인 프로젝터 (3단 구조) =================
def projector(x, y, z, r, ry):
    rot=(math.pi/2, 0, ry)
    # 외곽 알루미늄 링
    bpy.ops.mesh.primitive_torus_add(major_radius=r*1.35, minor_radius=0.035,
        location=(x,y,z), rotation=rot)
    setmat(bpy.context.object, m_dark_al); smooth(bpy.context.object)
    # 쉬라우드 (원통 하우징)
    bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=r*1.3, depth=0.34,
        location=(x, y+0.12, z), rotation=rot)
    c=bpy.context.object; setmat(c, m_bezel); smooth(c)
    # 크롬 리플렉터 콘
    bpy.ops.mesh.primitive_cone_add(vertices=64, radius1=r*1.22, radius2=r*0.45,
        depth=0.3, location=(x, y+0.10, z), rotation=rot)
    setmat(bpy.context.object, m_chrome); smooth(bpy.context.object)
    # 내부 배럴
    bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=r*0.5, depth=0.2,
        location=(x, y+0.05, z), rotation=rot)
    setmat(bpy.context.object, m_dark_al); smooth(bpy.context.object)
    # 유리 프로젝터 렌즈 (두꺼운 반구)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=64, ring_count=32, radius=r,
        location=(x, y-0.02, z))
    L=bpy.context.object; L.scale=(1,0.62,1); L.rotation_euler=(0,0,ry)
    setmat(L, m_projglass); smooth(L)
    # 발광 하프링 (상단 DRL 시그니처)
    bpy.ops.mesh.primitive_torus_add(major_radius=r*1.28, minor_radius=0.016,
        location=(x, y+0.02, z), rotation=rot)
    setmat(bpy.context.object, m_ring)
    # 방열 핀 (뒤쪽)
    for k in range(5):
        bpy.ops.mesh.primitive_cube_add(location=(x, y+0.30, z-r*0.9+k*r*0.45))
        f=bpy.context.object; f.scale=(r*1.1, 0.09, 0.012)
        f.rotation_euler=(0,0,ry)
        setmat(f, m_dark_al)

projector(-1.15, -0.34, 0.02, 0.28, math.radians(8))
projector(-0.35, -0.42, 0.00, 0.23, math.radians(4))

# ================= 픽셀 LED 매트릭스 모듈 =================
bpy.ops.mesh.primitive_cube_add(location=(0.55, -0.42, 0.05))
mod_frame = bpy.context.object
mod_frame.scale=(0.34, 0.1, 0.2)
bevel(mod_frame, 0.03, 4)
setmat(mod_frame, m_dark_al)
for gx in range(6):
    for gz in range(3):
        bpy.ops.mesh.primitive_cube_add(
            location=(0.32+gx*0.092, -0.50, 0.14-gz*0.095))
        px=bpy.context.object; px.scale=(0.032,0.02,0.032)
        on = random.random() > 0.25
        setmat(px, m_led if on else m_bezel)

# ================= 곡선 DRL 라이트 가이드 (J자형) =================
curve = bpy.data.curves.new("DRL",'CURVE'); curve.dimensions='3D'
sp = curve.splines.new('BEZIER'); sp.bezier_points.add(3)
pts=[(-1.6,-0.36,0.30),(-0.4,-0.50,0.33),(0.8,-0.50,0.30),(1.45,-0.38,0.05)]
for p,co in zip(sp.bezier_points, pts):
    p.co=co; p.handle_left_type=p.handle_right_type='AUTO'
curve.bevel_depth=0.028; curve.bevel_resolution=6
drl_obj = bpy.data.objects.new("DRL", curve)
bpy.context.collection.objects.link(drl_obj)
setmat(drl_obj, m_ring)

# ================= 앰버 방향지시등 스트립 (하단 곡선) =================
curve2 = bpy.data.curves.new("IND",'CURVE'); curve2.dimensions='3D'
sp2 = curve2.splines.new('BEZIER'); sp2.bezier_points.add(2)
for p,co in zip(sp2.bezier_points, [(-1.5,-0.34,-0.30),(0.0,-0.46,-0.32),(1.35,-0.34,-0.22)]):
    p.co=co; p.handle_left_type=p.handle_right_type='AUTO'
curve2.bevel_depth=0.024; curve2.bevel_resolution=5
ind_obj = bpy.data.objects.new("IND", curve2)
bpy.context.collection.objects.link(ind_obj)
setmat(ind_obj, m_amber)

# ================= 클리어 렌즈 커버 (곡면) =================
bpy.ops.mesh.primitive_cube_add(location=(0, -0.52, 0))
cov = bpy.context.object
cov.scale=(1.98, 0.07, 0.44)
bevel(cov, 0.14, 8)
sd = cov.modifiers.new("Bend",'SIMPLE_DEFORM')
sd.deform_method='BEND'; sd.angle=math.radians(-34); sd.deform_axis='Z'
setmat(cov, m_glass); smooth(cov)

# ================= 바닥 (반사면) =================
bpy.ops.mesh.primitive_plane_add(size=30, location=(0,0,-0.85))
gr = bpy.context.object
setmat(gr, mat("Floor",(0.03,0.03,0.035,1), rough=0.25, metallic=0.3))

# ================= 조명 =================
def light(loc, energy, size, rot):
    bpy.ops.object.light_add(type='AREA', location=loc, rotation=rot)
    L=bpy.context.object; L.data.energy=energy; L.data.size=size

light((3.5,-4.0,3.0), 900, 4, (math.radians(50),0,math.radians(40)))     # key
light((-4.0,-2.0,1.5), 300, 3, (math.radians(65),0,math.radians(-60)))   # fill
light((0.5, 2.5, 2.5), 500, 2, (math.radians(-45),0,0))                  # rim(뒤)
light((0,-2.0,4.5), 200, 6, (0,0,0))                                     # top soft

world = bpy.data.worlds.new("W"); scene.world=world; world.use_nodes=True
world.node_tree.nodes["Background"].inputs[0].default_value=(0.006,0.007,0.010,1)

# ================= 카메라 (3/4 로우앵글) =================
bpy.ops.object.camera_add(location=(2.9,-3.4,0.55),
    rotation=(math.radians(83),0,math.radians(41)))
cam=bpy.context.object; cam.data.lens=50
cam.data.dof.use_dof=True
cam.data.dof.focus_distance=4.0
cam.data.dof.aperture_fstop=4.5
scene.camera=cam

# ================= 렌더 =================
scene.render.engine='CYCLES'
scene.cycles.samples=48
scene.cycles.use_denoising=True
scene.cycles.device='CPU'
scene.render.resolution_x=1024
scene.render.resolution_y=576
scene.render.filepath="/home/claude/headlamp_v2.png"
scene.render.image_settings.file_format='PNG'
bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath="/home/claude/headlamp_v2.blend")
print("DONE")
