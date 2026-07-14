# CLAUDE.md

이 파일은 Claude Code가 이 리포지토리에서 작업할 때 참고하는 프로젝트 컨텍스트입니다.

## 프로젝트 개요

JLR(재규어랜드로버) 스타일 헤드램프를 Blender Python API(bpy)로 절차적(procedural)으로
모델링하고 헤드리스 환경에서 Cycles로 렌더링하는 프로젝트입니다.
GUI 없이 스크립트 실행만으로 모델 생성 → 렌더링 → .blend 저장까지 완료됩니다.

## 파일 구조

- `headlamp_v1.py` — 기본 버전: 슬림 가로형 하우징, 듀얼 프로젝터, DRL 바
- `headlamp_v2.py` — 고급 버전: 곡면 하우징(Bend/Taper), 3단 프로젝터 유닛,
  픽셀 LED 매트릭스, 베지어 커브 DRL 라이트 가이드, 방열 핀, DOF 카메라
- `headlamp_v2.blend` — v2 실행 결과로 저장된 Blender 씬 파일
- `renders/` — 렌더링 결과 이미지

## 실행 환경

- Python 3.11 (bpy 모듈은 3.11 전용 wheel 제공)
- `pip install bpy` → Blender 5.0.x가 파이썬 모듈로 설치됨
- GPU 불필요: Cycles CPU 렌더링 사용 (EEVEE는 헤드리스에서 GPU 컨텍스트 필요)

```bash
uv venv blenv --python 3.11
uv pip install bpy --python blenv/bin/python
blenv/bin/python headlamp_v2.py
```

## 코드 컨벤션

- 재질 생성은 `mat()` 헬퍼 사용 (Principled BSDF 기반)
- 유리 재질: Transmission Weight + IOR, blend_method='BLEND'
- 발광부(LED/DRL): Emission Color + Emission Strength
- 곡면 형태: SIMPLE_DEFORM(BEND/TAPER) 모디파이어 + Bevel 조합
- 라이트 가이드류: 베지어 커브 + bevel_depth
- 렌더 시간 관리: samples 32~48, 해상도 1024×576 이하 권장 (CPU 기준 2~3분)

## 주의 사항

- Blender 5.x에서 `use_nodes = True`는 DeprecationWarning 발생 (6.0에서 제거 예정)
- `Transmission Weight` 입력 이름은 Blender 4.0+ 기준 (구버전은 `Transmission`)
- JLR 실제 차량 디자인은 지적재산이므로 이 모델은 스타일을 참고한 오리지널 형상임
