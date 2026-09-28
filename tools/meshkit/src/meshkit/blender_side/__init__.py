"""Code that runs inside Blender, not in meshkit's own interpreter.

Nothing here is imported by meshkit itself: these files are handed to a
headless Blender as scripts (``job.py``) or loaded by path from within one
(``kinema_dae.py``). They depend on ``bpy``, which only exists in there.
"""
