from aiogram import Router

from . import basic, content, fallback

router = Router(name=__name__)
# order matters: fallback catches everything the others didn't
router.include_routers(basic.router, content.router, fallback.router)

__all__ = ["router"]
