import src.translation_processor as translation_processor


def test_translation_processor_imports_logging():
    assert hasattr(translation_processor, "logging")
