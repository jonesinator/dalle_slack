import sys
sys.path.append('.')

import dalle

def test_sanitize_prompt():
    source = "a lobster eating a salad"

    # Don't change anything
    r = dalle.sanitize_prompt(source, user='almost-everyone')
    assert r == source

    for user in ('matthew.moskowitz9',):
        # there are random numbers involved, so do it a few times for great success
        for _ in range(1000):
            r = dalle.sanitize_prompt(source, user=user)
            print(r)
            assert isinstance(r, str)
            assert r != source
