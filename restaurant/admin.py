from django.contrib import admin

from .models import (
    Article,
    Restaurant,
    RestaurantCategory,
    RestaurantImage,
    RestaurantMenu,
    Review,
    ReviewImage,
    SocialChannel,
    Tag,
)


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "title",
        "show_at_index",
        "is_published",
        "created_at",
        "modified_at",
    ]

    # 개별 객체를 추가하거나 수정할 때 보여줄 필드를 지정함(편집 화면에서 보임)
    # Admin에서 글을 생성하거나 수정할 때 이 필드들만 폼에 나타남(입력부분 밑에 안내하는 부분)
    fields = ["title", "preview_image", "content", "show_at_index", "is_published"]
    search_fields = ["title"]
    list_filter = ["show_at_index", "is_published"]
    date_hierarchy = "created_at"
    actions = ["make_published"]

    @admin.action(description="선택한 컬럼을 공개상태로 변경합니다.")
    def make_published(self, request, queryset):
        queryset.update(is_published=True)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["id", "name"]
    fields = ["name"]
    search_fields = ["name"]


class RestaurantMenuInline(admin.TabularInline):
    model = RestaurantMenu
    extra = 1


class RestaurantImageInline(admin.TabularInline):
    model = RestaurantImage
    extra = 1


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
        "branch_name",
        "is_closed",
        "phone",
        "rating",
        "rating_count",
    ]
    fields = [
        "name",
        "branch_name",
        "category",
        "is_closed",
        "phone",
        "latitude",
        "longitude",
        "tags",
    ]
    readonly_fields = ["rating", "rating_count"]
    search_fields = ["name", "branch_name"]
    list_filter = ["tags"]
    autocomplete_fields = ["tags"]
    inlines = [RestaurantMenuInline, RestaurantImageInline]

    # 인스턴스를 생성할때 인라인 표시 안하도록
    def get_inline_instances(self, request, obj=None):
        return obj and super().get_inline_instances(request, obj) or []


@admin.register(RestaurantCategory)
class RestaurantCategoryIAdmin(admin.ModelAdmin):
    list_display = ["name"]
    fields = ["cuisine_type", "name"]


class ReviewImageInline(admin.TabularInline):
    model = ReviewImage
    extra = 1


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ["id", "restaurant_name", "author", "rating", "content_partial"]
    inlines = [ReviewImageInline]

    # 인스턴스를 생성할때 인라인 표시 안하도록
    def get_inline_instances(self, request, obj=None):
        return obj and super().get_inline_instances(request, obj) or []


@admin.register(SocialChannel)
class SocialChannelAdmin(admin.ModelAdmin):
    list_display = ["id", "name"]
    fields = ["name"]
