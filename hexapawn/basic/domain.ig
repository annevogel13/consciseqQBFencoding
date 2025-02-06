#blackactions
:action forwardBlack
:parameters (?x, ?y)
:precondition (black(?x,?y+1) open(?x,?y))
:effect (open(?x,?y+1) black(?x,?y))
#whiteactions
:action forwardWhite
:parameters (?x, ?y)
:precondition (white(?x,?y-1) open(?x,?y))
:effect (open(?x,?y-1) white(?x,?y))