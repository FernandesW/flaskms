from flask import Blueprint, jsonify, request

from src.constants.http_status_codes import (
    HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_201_CREATED)
import validators
from src.database import Bookmark, db, BookmarkSchema
from flask_jwt_extended import get_jwt_identity, jwt_required
bookmarks = Blueprint("bookmarks", __name__, url_prefix="/api/v1/bookmarks")


@bookmarks.route('/', methods=["GET", "POST"])
@jwt_required()
def handle_bookmarks():
    if request.method == "POST":
        body = request.get_json().get('body', '')
        url = request.get_json().get('url', '')
        if not validators.url(url):
            return jsonify(
                {
                    'error': 'Enter a valid URL',
                }
            ), HTTP_400_BAD_REQUEST
        if Bookmark.query.filter_by(url=url).first():
            return jsonify(
                {
                    'error': 'URL already exists',
                }
            ), HTTP_400_BAD_REQUEST
        bookmark = Bookmark(url=url, body=body, user_id=get_jwt_identity())
        bookmark_output = BookmarkSchema().dump(bookmark)
        db.session.add(bookmark)
        db.session.commit()
        return jsonify(
            {
                "data": bookmark_output
            }
        ), HTTP_201_CREATED

    else:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 5, type=int)
        bookmark_query = Bookmark.query.filter_by(
            user_id=get_jwt_identity()).paginate(page=page, per_page=per_page)

        bookmark_output = BookmarkSchema(many=True).dump(bookmark_query)
        meta = {
            "page":bookmark_query.page,
            "pages":bookmark_query.pages,
            "total_count":bookmark_query.total,
            "prev_page":bookmark_query.prev_num,
            "next_page":bookmark_query.next_num,
            "has_next":bookmark_query.has_next,
            "has_prev":bookmark_query.has_prev
        }
        return jsonify({
            "data": bookmark_output,
            "meta": meta
        }), HTTP_200_OK
