a = 2
b = 3
t = a > 0
if t then goto L6
goto L7
L6: x = 2 * a
y = 2 * b
goto L4
L7: x = 3 * a
y = 3 * b
L4: noOp
L10: if t then goto L11
goto L5
L11: a+=1
goto L10
L5: 
