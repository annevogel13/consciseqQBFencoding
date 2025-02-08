% python Q-sage.py --ib_problem hexapawn/basic/3x3_hexapawn_black_diag_forwards.ig -e ib --game_type general --run 2 --encoding_out intermediate_files/encoding/hexapawn.txt --ib_domain hexapawn/basic/domain.ig
%   y
%   3   b   -   b 
%   2   -   -   - 
%   1   w   -   w 
%       1   2   3   x
#boardsize
3 3
#depth
3
#times
t1,t2
#init
(black(3,3))
#blackgoal
(black(?x,1))
#whitegoal