from curvinspect.synthetic import (
    create_defective_part_image,
    create_normal_part_image,
    save_demo_images,
)


def test_create_normal_part_image_has_expected_shape():
    image = create_normal_part_image(size=256)

    assert image.shape == (256, 256, 3)


def test_create_defective_part_image_has_expected_shape():
    image = create_defective_part_image(size=256)

    assert image.shape == (256, 256, 3)


def test_save_demo_images_creates_files(tmp_path):
    paths = save_demo_images(tmp_path)

    assert paths["normal"].exists()
    assert paths["defective"].exists()