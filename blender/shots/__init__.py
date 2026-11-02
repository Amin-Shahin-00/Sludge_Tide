"""Shot registry: each chapter module registers one builder per shot id."""
REG = {}
PREVIEW = {}


def shot(sid, preview=(0.5,)):
    def deco(fn):
        REG[sid] = fn
        PREVIEW[sid] = preview
        return fn
    return deco


def load_all():
    import importlib
    for m in ("ch1_night", "ch2_bloom", "ch3_scrap", "ch4_rust", "ch5_truth", "ch6_speech", "ch7_battle", "ch8_end"):
        try:
            importlib.import_module(f"shots.{m}")
        except ModuleNotFoundError as e:
            if m not in str(e):
                raise
            print("(missing chapter module)", m)
