% python Q-sage.py --ib_problem hexapawn/basic/3x3_hexapawn_black_diag_right.ig -e ib --game_type general --run 2 --encoding_out intermediate_files/encoding/hexapawn.txt --ib_domain hexapawn/basic/domain.ig
%   y
%   3   -   b   -
%   2   -   -   w 
%   1   -   -   - 
%       1   2   3   x
#boardsize
3 3
#depth
3
#times
t1 t2 t3
#init
(white(3,2) black(2,3))
#blackgoal
(black(?x,1))
#whitegoal
(white(?x,3))