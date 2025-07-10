from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.forms import ValidationError


class Article(models.Model):
    title = models.CharField(max_length=100, db_index=True)
    preview_image = models.ImageField(null=True, blank=True)
    content = models.TextField()
    show_at_index = models.BooleanField(
        default=False
    )  # 인덱스에서 보여줄것인가. 기본값은 표시안함
    is_published = models.BooleanField(default=False)  # 칼럼을 사용자에게 노출할지 여부
    created_at = models.DateTimeField(
        "생성일", auto_now_add=True
    )  # 프론트엔드 페이지가 아닌 관리자페이지에서 보려고
    modified_at = models.DateTimeField("수정일", auto_now_add=True)

    class Meta:
        verbose_name = "칼럼"
        verbose_name_plural = "칼럼s"

    def __str__(self):
        return f"{self.id} - {self.title}"


class Restaurant(models.Model):
    name = models.CharField(
        "음식이름", max_length=100, db_index=True
    )  # 음식이름, 검색할 수 있기때문에 속도를 위해 index=True
    branch_name = models.CharField(
        "지점",
        max_length=100,
        db_index=True,
        null=True,
        blank=True,  # blank 사용자, null 데이타
    )  # 지점
    description = models.TextField("설명", null=True, blank=True)
    address = models.CharField("주소", max_length=255, db_index=True)
    feature = models.CharField("특징", max_length=255, null=True, blank=True)
    is_closed = models.BooleanField(
        "폐업여부", default=False
    )  # 실제 웹에는 없다. 관리자만 보도록 default=False
    latitude = models.DecimalField(
        "위도",
        max_digits=16,  # 소수점포함 숫자자릿점 38.01215654
        decimal_places=12,  # 소수점 이하 자릿수
        db_index=True,  # 데이터 읽어올때 속도를 위해
        default="0.0000",
    )
    longitude = models.DecimalField(
        "경도",
        max_digits=16,
        decimal_places=12,
        db_index=True,  # 데이터 읽어올때 속도를 위해
        default="0.0000",
    )
    phone = models.CharField(
        "전화번호",
        max_length=16,
        help_text="E.164 포맷",  # ex) +821033333333
    )
    rating = models.DecimalField(
        "평점",
        max_digits=3,
        decimal_places=2,  # 소수점 둘째자리까지 가능 : 최대 9.99
        default="0.0",
    )
    rating_count = models.PositiveIntegerField("평가수", default=0)
    start_time = models.TimeField("영업시작시간", null=True, blank=True)
    end_time = models.TimeField("영업종료시간", null=True, blank=True)
    last_order_time = models.TimeField("라스트 오더 시간", null=True, blank=True)
    category = models.ForeignKey(
        "RestaurantCategory",
        on_delete=models.SET_NULL,  # 참조된 카테고리가 삭제시 Null로 설정됨(데이터 보존)
        null=True,
        blank=True,
    )
    tags = models.ManyToManyField(
        "Tag",
        blank=True,
    )  # M:N 관계
    region = models.ForeignKey(
        "restaurant.Region",  # 첫번째참조 restaurant, 테이블명 Region 추가(앱이름.모델클래스명)
        on_delete=models.SET_NULL,  # 참조된 카테고리가 삭제시 Null로 설정됨(데이터 보존)
        null=True,
        blank=True,
        db_index=True,
        verbose_name="지역",
        related_name="restaurants",  # related_name : 역참조 이름 설정(쿼리 날릴 때 필요하고 중요하다)
    )
    # 레스토랑 지역 region.restaurants.all() 레스토랑보다 지역이 더 큰 범위

    class Meta:
        verbose_name = "레스토랑"
        verbose_name_plural = "레스토랑s"

    def __str__(self):
        return f"{self.name}{self.branch_name}" if self.branch_name else self.name

    # 지점명이 있으면 이름과 지점명을 반환해주고, 없으면 식당이름만 반환해주고


class CuisineType(models.Model):
    name = models.CharField("이름", max_length=20)

    class Meta:
        verbose_name = "음식종류"
        verbose_name_plural = "음식종류s"

    def __str__(self):
        return self.name


class RestaurantCategory(models.Model):
    name = models.CharField("이름", max_length=20)
    cuisineType = models.ForeignKey(
        "CuisineType",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "레스토랑 카테고리"
        verbose_name_plural = "레스토랑 카테고리s"

    def __str__(self):
        return self.name


class RestaurantImage(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    is_representative = models.BooleanField(
        "대표 이미지 여부", default=False
    )  # 업데이트된 이미지를 대표이미지로 분류처리
    order = models.PositiveIntegerField("순서", null=True, blank=True)
    name = models.CharField("이름", max_length=100, null=True, blank=True)
    image = models.ImageField("이미지", max_length=100, upload_to="restaurant")
    # 사용자가 이미지를 업로드하면 ROOT/restaurant/ 폴더 아래 이미지 파일이 저장됐다. restaurant폴더 자동생성
    created_at = models.DateTimeField("생성일", auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField("수정일", auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "레스토랑 이미지"
        verbose_name_plural = "레스토랑 이미지s"

    def __str__(self):
        return f"{self.id}:{self.image}"

    # 대표이미지를 2개 이상 지정하지 못하도록 막는코드를 작성(오버라이딩방식)
    # 장고에 있는 기능이면 @로 쓰지만, 지금은 없는 기능이라 직접 작성한다.
    def clean(self):
        images = self.restaurant.restaurantimage_set.filter(is_representative=True)
        # .restaurantimage_set : 해당 Restaurant 연결된 모든 이미지들
        # .filter() : 괄호 안 조건에 맞는 것 필터링

        if self.is_representative and images.exclude(id=self.id).count() > 0:
            raise ValidationError("대표 이미지는 하나만 설정할 수 있습니다.")
        # 현재 이미지가 대표이미지이고, 현재이미지를 제외한 다른 이미지들이 1개 이상 존재한다면


class RestaurantMenu(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    name = models.CharField("이름", max_length=100)
    price = models.PositiveIntegerField("가격", default=0)
    image = models.ImageField(
        "이미지",
        upload_to="restaurant-menu",
        null=True,
        blank=True,
    )  # 장고는 세팅먼저 찾고 다음으로 여기찾고 없으면 만든다. # MEDIA_ROOT/restaurant-menu/이미지 파일을 저장
    created_at = models.DateTimeField("생성일", auto_now_add=True)
    updated_at = models.DateTimeField("수정일", auto_now_add=True)

    class Meta:
        verbose_name = "레스토랑 메뉴"
        verbose_name_plural = "레스토랑 메뉴s"

    def __str__(self):
        return self.name


class Review(models.Model):
    title = models.CharField("제목", max_length=100)
    author = models.CharField("작성자", max_length=100)
    profile_image = models.ImageField(
        "프로필이미지",
        upload_to="review-profile",
        null=True,
        blank=True,
    )
    content = models.TextField("내용")
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )  # 양의정수 허용되는 필드값의 범위를 0~30,000 가능하다. 실제사용 1~5
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    social_channel = models.ForeignKey(
        "SocialChannel",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField("생성일", auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField("수정일", auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "리뷰"
        verbose_name_plural = "리뷰s"

    def __str__(self):
        return f"{self.author}:{self.title}"


class ReviewImage(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    image = models.ImageField(max_length=100, upload_to="review")
    created_at = models.DateTimeField("생성일", auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField("수정일", auto_now=True, db_index=True)

    class Meta:
        verbose_name = "리뷰이미지"
        verbose_name_plural = "리뷰이미지s"

    def str(self):
        return f"{self.id}:{self.image}"


class ReviewImage(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    image = models.ImageField(max_length=100, upload_to="review")


class SocialChannel(models.Model):
    name = models.CharField("이름", max_length=100)

    class Meta:
        verbose_name = "소셜채널"
        verbose_name_plural = "소셜채널s"

    def str(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(
        "이름", max_length=100, unique=True
    )  # 이 필드는 중복을 허용하지 않음

    class Meta:
        verbose_name = "태그"
        verbose_name_plural = "태그s"

    def str(self):
        return self.name


class Region(models.Model):
    sido = models.CharField("광역시도", max_length=20)
    sigungu = models.CharField("시군구", max_length=20)
    eupmyeondong = models.CharField("읍면동", max_length=20)

    class Meta:
        verbose_name = "지역"
        verbose_name_plural = "지역s"
        unique_together = ("sido", "sigungu", "eupmyeondong")

    def str(self):
        return f"{self.sido} {self.sigungu} {self.eupmyeondong}"
