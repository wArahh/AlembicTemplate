from fluent_compiler.bundle import FluentBundle
from fluentogram import FluentTranslator, TranslatorHub


def create_translator_hub() -> TranslatorHub:
    translator_hub = TranslatorHub(
        locales_map={
            "en": ("en",),
        },
        translators=[
            FluentTranslator(
                locale="en",
                translator=FluentBundle.from_files(
                    locale="en-US",
                    filenames=["app/locales/en/LC_MESSAGES/txt.ftl"]
                ),
            ),
        ],
        root_locale="en"
    )
    return translator_hub


translator_hub = create_translator_hub()
i18n = translator_hub.get_translator_by_locale(locale='en')
