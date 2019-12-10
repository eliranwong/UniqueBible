# To install:

pip3 install diff-match-patch

# To test:

>>> from diff_match_patch import diff_match_patch
>>> dmp = diff_match_patch()
>>> diff = dmp.diff_main("test1", "test2")
>>> html = dmp.diff_prettyHtml(diff)
>>> html
'<span>test</span><del style="background:#ffe6e6;">1</del><ins style="background:#e6ffe6;">2</ins>'

Read more:

https://github.com/google/diff-match-patch/wiki/API
