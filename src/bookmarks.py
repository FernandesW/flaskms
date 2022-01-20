from flask import Blueprint, jsonify, request
from flasgger import swag_from
from src.constants.http_status_codes import (
    HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_201_CREATED, HTTP_404_NOT_FOUND,
    HTTP_204_NO_CONTENT)
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

        bookmark_output = BookmarkSchema(many=True).dump(bookmark_query.items)
        meta = {
            "page": bookmark_query.page,
            "pages": bookmark_query.pages,
            "total_count": bookmark_query.total,
            "prev_page": bookmark_query.prev_num,
            "next_page": bookmark_query.next_num,
            "has_next": bookmark_query.has_next,
            "has_prev": bookmark_query.has_prev
        }
        return jsonify({
            "data": bookmark_output,
            "meta": meta
        }), HTTP_200_OK


@bookmarks.route('/<int:id>', methods=["GET"])
@jwt_required()
def get_bookmark(id):
    current_user = get_jwt_identity()
    bookmark = Bookmark.query.filter_by(user_id=current_user, id=id).first()
    bookmark_output = BookmarkSchema().dump(bookmark)
    if not bookmark:
        return jsonify(
            {
                'error': 'Bookmark not found',
            }
        ), HTTP_404_NOT_FOUND

    return jsonify(bookmark_output
                   ), HTTP_200_OK


@bookmarks.route('/<int:id>', methods=["PUT", "PATCH"])
@jwt_required()
def edit_bookmark(id):
    current_user = get_jwt_identity()
    bookmark = Bookmark.query.filter_by(user_id=current_user, id=id).first()
    if not bookmark:
        return jsonify(
            {
                'error': 'Bookmark not found',
            }
        ), HTTP_404_NOT_FOUND

    body = request.get_json().get('body', '')
    url = request.get_json().get('url', '')
    if not validators.url(url):
        return jsonify(
            {
                'error': 'Enter a valid URL',
            }
        ), HTTP_400_BAD_REQUEST

    bookmark.url = url
    bookmark.body = body
    bookmark_output = BookmarkSchema().dump(bookmark)
    db.session.commit()
    return jsonify({
        "Success": "Updated",
        "data": bookmark_output
    }), HTTP_200_OK


@bookmarks.route('/<int:id>', methods=["DELETE"])
@jwt_required()
def delete_bookmark(id):
    current_user = get_jwt_identity()
    bookmark = Bookmark.query.filter_by(user_id=current_user, id=id).first()
    if not bookmark:
        return jsonify(
            {
                'error': 'Bookmark not found',
            }
        ), HTTP_404_NOT_FOUND
    db.session.delete(bookmark)
    db.session.commit()
    bookmark_output = BookmarkSchema().dump(bookmark)

    return jsonify({
        "Success": "Deleted"
    }), HTTP_204_NO_CONTENT


@bookmarks.route('/stats', methods=["GET"])
@jwt_required()
@swag_from("docs/bookmarks/stats.yaml")
def get_stats():
    current_user = get_jwt_identity()
    
    data = []
    items = Bookmark.query.filter_by(user_id=current_user)
    bookmark_output=BookmarkSchema(many=True,only=("visits","url","id","short_url")).dump(items)
    return jsonify({"data":bookmark_output})

