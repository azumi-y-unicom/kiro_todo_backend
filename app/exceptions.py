"""
カスタム例外ハンドラー

FastAPIアプリケーション用のカスタム例外ハンドラーを定義する。
404、422、500エラーの適切な処理を実装する。
"""
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
import logging

from app.services.todo import TodoNotFoundError, TodoValidationError, TodoDatabaseError

logger = logging.getLogger(__name__)


async def todo_not_found_handler(request: Request, exc: TodoNotFoundError) -> JSONResponse:
    """
    ToDoアイテムが見つからない場合の例外ハンドラー
    
    Args:
        request (Request): FastAPIリクエストオブジェクト
        exc (TodoNotFoundError): ToDoアイテムが見つからない例外
        
    Returns:
        JSONResponse: 404エラーレスポンス
    """
    logger.warning(f"Todo not found: {exc}")
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "detail": str(exc),
            "error_type": "not_found",
            "todo_id": exc.todo_id
        }
    )


async def todo_validation_error_handler(request: Request, exc: TodoValidationError) -> JSONResponse:
    """
    ToDoアイテムのバリデーションエラーの例外ハンドラー
    
    Args:
        request (Request): FastAPIリクエストオブジェクト
        exc (TodoValidationError): バリデーションエラー例外
        
    Returns:
        JSONResponse: 422エラーレスポンス
    """
    logger.warning(f"Todo validation error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": str(exc),
            "error_type": "validation_error"
        }
    )


async def todo_database_error_handler(request: Request, exc: TodoDatabaseError) -> JSONResponse:
    """
    ToDoアイテムのデータベースエラーの例外ハンドラー
    
    Args:
        request (Request): FastAPIリクエストオブジェクト
        exc (TodoDatabaseError): データベースエラー例外
        
    Returns:
        JSONResponse: 500エラーレスポンス
    """
    logger.error(f"Todo database error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error occurred",
            "error_type": "database_error",
            "message": str(exc)
        }
    )


def _serialize_validation_errors(errors):
    """
    バリデーションエラーをJSON serializable形式に変換する
    
    Args:
        errors: バリデーションエラーのリスト
        
    Returns:
        list: JSON serializable形式のエラーリスト
    """
    serialized_errors = []
    for error in errors:
        serialized_error = {}
        for key, value in error.items():
            if isinstance(value, bytes):
                try:
                    serialized_error[key] = value.decode('utf-8')
                except UnicodeDecodeError:
                    serialized_error[key] = str(value)
            else:
                serialized_error[key] = value
        serialized_errors.append(serialized_error)
    return serialized_errors


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    FastAPIのリクエストバリデーションエラーの例外ハンドラー
    
    Args:
        request (Request): FastAPIリクエストオブジェクト
        exc (RequestValidationError): リクエストバリデーションエラー
        
    Returns:
        JSONResponse: 422エラーレスポンス
    """
    logger.warning(f"Request validation error: {exc}")
    
    # リクエストボディがbytesの場合は文字列に変換
    body = exc.body
    if isinstance(body, bytes):
        try:
            body = body.decode('utf-8')
        except UnicodeDecodeError:
            body = str(body)
    
    # エラー詳細をJSON serializable形式に変換
    serialized_errors = _serialize_validation_errors(exc.errors())
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": serialized_errors,
            "error_type": "request_validation_error",
            "body": body
        }
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    HTTPExceptionの例外ハンドラー
    
    Args:
        request (Request): FastAPIリクエストオブジェクト
        exc (HTTPException): HTTP例外
        
    Returns:
        JSONResponse: HTTPエラーレスポンス
    """
    logger.warning(f"HTTP exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "error_type": "http_error",
            "status_code": exc.status_code
        }
    )


async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """
    SQLAlchemyエラーの例外ハンドラー
    
    Args:
        request (Request): FastAPIリクエストオブジェクト
        exc (SQLAlchemyError): SQLAlchemyエラー
        
    Returns:
        JSONResponse: 500エラーレスポンス
    """
    logger.error(f"SQLAlchemy error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Database operation failed",
            "error_type": "database_error"
        }
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    一般的な例外の例外ハンドラー
    
    Args:
        request (Request): FastAPIリクエストオブジェクト
        exc (Exception): 一般的な例外
        
    Returns:
        JSONResponse: 500エラーレスポンス
    """
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An unexpected error occurred",
            "error_type": "internal_server_error"
        }
    )


def register_exception_handlers(app):
    """
    FastAPIアプリケーションに例外ハンドラーを登録する
    
    Args:
        app: FastAPIアプリケーションインスタンス
    """
    app.add_exception_handler(TodoNotFoundError, todo_not_found_handler)
    app.add_exception_handler(TodoValidationError, todo_validation_error_handler)
    app.add_exception_handler(TodoDatabaseError, todo_database_error_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_error_handler)
    app.add_exception_handler(Exception, general_exception_handler)
    
    logger.info("Exception handlers registered successfully")