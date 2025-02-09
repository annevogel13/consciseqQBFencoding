#blackactions
:action setQueen
:parameters (?x, ?y)
:precondition (open(?x,?y) open(?x-1,?y) open(?x+1,?y) open(?x+2,?y) open(?x,?y+1) open(?x,?y-1) open(?x,?y-2))
:effect (black(?x,?y))
:action setQueen2
:parameters (?x, ?y)
:precondition (open(?x,?y) open(?x-1,?y) open(?x-2,?y) open(?x+1,?y) open(?x,?y+1) open(?x,?y+2) open(?x,?y-1))
:effect (black(?x,?y))
:action setQueen3
:parameters (?x, ?y)
:precondition (open(?x,?y) open(?x-1,?y) open(?x-2,?y) open(?x+1,?y) open(?x,?y-3) open(?x,?y-2) open(?x,?y-1))
:effect (black(?x,?y))
#whiteactions
:action doNothing
:parameters (?x, ?y)
:precondition (open(?x,?y))
:effect (open(?x,?y))