#!/bin/sh

maturin develop # Builds the library, puts it in local scope.

cat > example.code <<EOF

        Test 1: This is a single line comment

                start->// test

        Test 2: This is a multi-line comment.

1
2               start->/*
3                       * test
4                       */<-end
5

EOF

python3 <<EOF

import rcmpy

with open("example.code", 'r') as file:
    code = file.read()

print("\nExample File",			code);
print("\nkeep newlines+spaces:",	rcmpy.keep_newlines_spaces(code));
print("\nkeep newlines:",		rcmpy.keep_newlines(code));
print("\nkeep nothing: (THIS CHANGES LINECOUNT)",		rcmpy.keep_nothing(code));
EOF

rm example.code
