
% python Q-sage.py --ib_problem hexapawn/3x3_1move_left_case1.ig -e ib --game_type general --run 2 --encoding_out intermediate_files/encoding/hexapawn.txt --ib_domain hexapawn/domain.ig
%   y
%   3   -   -   -            
%   2   -   b   -         
%   1   w   w   -         
%       1   2   3   x
#boardsize
3 3
#depth
3
#times
t1 t2 t3
#init
(black(1,2) white(1,1) white(2,1))
#blackgoal
(black(?x,1))
#whitegoal
(white(?x,3))