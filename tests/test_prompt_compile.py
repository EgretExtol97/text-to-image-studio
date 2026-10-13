from text_to_image_studio.processors.prompt import compile_prompt


def test_default_negative_applied():
    pos, neg = compile_prompt("a cat", "")
    assert pos == "a cat"
    assert "blurry" in neg


def test_negative_passthrough():
    _, neg = compile_prompt("a cat", "extra fingers")
    assert neg == "extra fingers"


def test_weight_syntax_preserved():
    pos, _ = compile_prompt("(cyberpunk city:1.3)", "")
    assert "(cyberpunk city:1.3)" in pos


def test_truncation_caps_words():
    long_prompt = " ".join(["word"] * 500)
    pos, _ = compile_prompt(long_prompt, "")
    assert len(pos.split()) == 75 * 3
<<<