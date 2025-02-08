
% python Q-sage.py --ib_problem hexapawn/3x3_1move_left_case2.ig -e ib --game_type general --run 2 --encoding_out intermediate_files/encoding/hexapawn.txt --ib_domain hexapawn/domain.ig
%   y
%   3   -   -   b            
%   2   b   w   -         
%   1   -   w   w         
%       1   2   3   x
#boardsize
3 3
#depth
3
#times
t1 t2 t3
#init
(black(1,2) black(3,3) white(2,1) white(2,2) white(3,1))
#blackgoal
(black(?x,1))
#whitegoal
(white(?x,3))