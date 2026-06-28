from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.exceptions import DocumentNotFound, UnsupportedFileType


def register_error_handlers(app):
    @app.exception_handler(DocumentNotFound)
    async def document_not_found_handler(request: Request, exc: DocumentNotFound):
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(UnsupportedFileType)
    async def unsupported_file_type_handler(request: Request, exc: UnsupportedFileType):
        return JSONResponse(status_code=415, content={"detail": str(exc)})
