#whiteactions
%action1
:action forward
:parameters (?x, ?y)
:precondition (white(?x,?y) open(?x,?y+1))
:effect (white(?x,?y+1) open(?x,?y))
%action 2 
:action capturediagleft
:parameters (?x, ?y)
:precondition (white(?x,?y) black(?x-1,?y+1))
:effect (open(?x,?y) white(?x-1,?y+1))
%action 3 
:action captureddiagright
:parameters (?x, ?y)
:precondition (white(?x,?y) black(?x+1,?y+1))
:effect (open(?x,?y) white(?x+1,?y+1))
#blackactions
%action1
:action forward
:parameters (?x, ?y)
:precondition (black(?x,?y)open(?x,?y-1))
:effect (white(?x,?y-1) open(?x,?y))
%action 2 
:action capturediagleft
:parameters (?x, ?y)
:precondition (black(?x,?y) white(?x-1,?y-1))
:effect (open(?x,?y) black(?x-1,?y-1))
%action 3 
:action capturediagright
:parameters (?x, ?y)
:precondition (black(?x,?y) white(?x+1,?y-1))
:effect (open(?x,?y) black(?x+1,?y-1))