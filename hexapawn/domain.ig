#blackactions
:action forwardBlack
:parameters (?x, ?y)
:precondition (black(?x,?y+1) open(?x,?y))
:effect (open(?x,?y+1) black(?x,?y))
:action diagBlackRight
:parameters (?x, ?y)
:precondition (black(?x-1,?y+1) white(?x,?y))
:effect (black(?x,?y) open(?x-1,?y+1))
:action diagBlackLeft
:parameters (?x, ?y)
:precondition (black(?x+1,?y+1) white(?x,?y))
:effect (black(?x,?y) open(?x+1,?y+1))
#whiteactions
:action forwardWhite
:parameters (?x, ?y)
:precondition (white(?x,?y-1) open(?x,?y))
:effect (open(?x,?y-1) white(?x,?y))
:action diagWhiteRight
:parameters (?x, ?y)
:precondition (black(?x-1,?y-1) black(?x,?y))
:effect (open(?x-1,?y-1) white(?x,?y))
:action diagWhiteLeft
:parameters (?x, ?y)
:precondition (black(?x+1,?y-1) black(?x,?y))
:effect (open(?x+1,?y-1) white(?x,?y))