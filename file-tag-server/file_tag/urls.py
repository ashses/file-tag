from file_tag_app import views
from fastapi import APIRouter

router = APIRouter()

router.add_api_route("/tag/create", views.create_tag_view, methods=["POST"])
router.add_api_route("/tag/update", views.update_tag_view, methods=["PUT"])
router.add_api_route("/tag/delete/{tag_id}", views.delete_tag_view, methods=["DELETE"])
router.add_api_route("/tag/get", views.get_tag_view, methods=["GET"])
router.add_api_route("/file/create", views.create_file_view, methods=["POST"])
router.add_api_route("/file/multi/create", views.create_multi_file_view, methods=["POST"])
router.add_api_route("/file/get", views.get_file_list_view, methods=["GET"]) # 测试用的
router.add_api_route(r"/file/delete/{file_id}", views.delete_file_view, methods=["DELETE"])
router.add_api_route("/tag/search/", views.search_tag_view, methods=["GET"])
router.add_api_route("/file/update", views.update_file_tags_view, methods=["PUT"])
router.add_api_route("/file/info/update", views.update_file_view, methods=["PUT"])
router.add_api_route("/tag/single/get", views.get_a_tag_view, methods=["GET"])
router.add_api_route("/file/search", views.search_file_view, methods=["GET"])
