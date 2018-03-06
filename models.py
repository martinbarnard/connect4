from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.db import models

# This will give us absolute co-ords for our coin
abs_dirs = lambda dirs, x, y : [((n[0]) + x, (n[1]) + y) for n in dirs]

# ###############################################################################
# Map our input directions to our relative-from-coin co-ords
# This could really be improved, but it will work for now
# Excuse the paranoid spacing issues - too much TCL
# ###############################################################################
dir_mappings = {
    'horizontal': ['horiz_r',  'horiz_l' ],
    'vertical'  : ['vertical'            ],
    'diagonal_l': ['diag_u_r', 'diag_d_l'],
    'diagonal_r': ['diag_u_l', 'diag_d_r']
}

# These are relative offsets from given coin co-ords
directions = {
    'horiz_r'   : [( 0, 1), ( 0, 2), ( 0, 3)],
    'horiz_l'   : [( 0,-1), ( 0,-2), ( 0,-3)],
    'diag_u_r'  : [( 1, 1), ( 2, 2), ( 3, 3)],
    'diag_d_l'  : [(-1,-1), (-2,-2), (-3,-3)],
    'diag_d_r'  : [( 1,-1), ( 2,-2), ( 3,-3)],
    'diag_u_l'  : [(-1, 1), (-2, 2), (-3, 3)],
    'vertical'  : [(-1, 0), (-2, 0), (-3, 0)],
}

@python_2_unicode_compatible
class GameManager(models.Manager):
    def active_games(self):
        '''
        Will return any games with state of 'active'
        '''
        return self.Games.objects.filter(status='active')

@python_2_unicode_compatible
class Game(models.Model):
    '''
    according to __str__, we are returning the string rep both players, or some shiny text to tempt 
    the wandering player to join as player 2
    '''
    player1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='player_1')
    player2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='player_2', blank=True, null=True)
    status = models.CharField(max_length=10, default='active')

    winner = models.CharField(max_length=10)
    created_date = models.DateTimeField(default=timezone.now)
    # Manager
    objects = models.Manager()
    active_games = GameManager()

    def __str__(self):
        if self.player2:
            return ' vs '.join([self.player1.get_full_name(), self.player2.get_full_name()])
        else:
            return 'Join now to play {}'.format(self.player1.get_short_name())

    @property
    def start_date(self):
        return self.coin_set.order_by('created_date')[0].created_date

    @property
    def last_move(self):
        return self.coin_set.order_by('-created_date')[0]

    @property
    def last_action_date(self):
        return self.last_move.created_date

    @property
    def is_winner(self):
        '''
        Will return True if we have a winning move (make_move)
        '''
        for d in ['horizontal', 'vertical'  , 'diagonal_l', 'diagonal_r']:
            n = self.calculate_neighbours(d)
            if n >= 3:
                return True
        return False
    
    def is_nbr(self, depth, player, coords):
        '''
        Will return how many matches from our array were hits.
        -- RECURSIVE --
        '''
        if len(coords) > depth:
            coin = self.coin_set.filter(player=player) \
                            .filter(x=coords[depth][0])\
                            .filter(y=coords[depth][1])


            if len(coin)  >0:
                return self.is_nbr(depth+1, player, coords)
            else:
                return depth
        else:
            return depth

    def calculate_neighbours(self, direction):
        '''
        Will calculate the neighbours of the last coin
        direction in (horizontal/vertical/diagonal_l/diagonal_r)
        will return an int. >2 means a row
        '''

        if direction not in dir_mappings:
            # Should raise error to indicate shenanigans here!
            return 0

        total_nbrs  = 0          # Return value
        coin        = self.last_move
        player      = coin.player

        # Assume we have a direction
        dirs = dir_mappings[direction]

        # Get our absolute co-ords and pass them to our recursive tester
        for d in dirs:
            dd = directions[d] # finally get to our relative points 
            abs_coords = abs_dirs(dd, coin.x, coin.y)
            total_nbrs += self.is_nbr(0, player, abs_coords)

        return total_nbrs

    def join_up(self, player_2):
        if self.player2 is None:
            self.player2 = player_2
            self.save()
            return True
        else:
            return False

    def make_move(self, player,column):
        '''
        We should just be doing a column, and filter number of objects in col already.
        Since we cannot slip a coin under the previous one in the col
        '''
        # From wikipedia
        max_columns = 7
        max_rows    = 6

        if column < 1 or column > max_columns:
            # TODO: Raise OOB exception?
            return False
            

        # We need to get the number of coins on the column and our row is that +1 
        # TODO: Confirm zero-or-one indexing in our calculations
        num_rows_for_col = self.coin_set.filter(x=column)
        row_len = len(num_rows_for_col)

        if num_rows_for_col < 1 or row_len > max_rows:
            # TODO: Raise OOB exception?
            return False

        try:
             self.coin_set.create(game=self, player=player, y=row_len, x=column)
        except:
             return False

        return True

@python_2_unicode_compatible
class Coin(models.Model):
    '''
    Note. Renamed column & row as they are reserved in some SQL engines
    '''
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    # x is column, y is row
    x = models.IntegerField()
    y = models.IntegerField()
    created_date = models.DateTimeField(default=timezone.now)

    # And this is why I don't like everything-must-be-a-class mentality!
    def __str__(self):
        return ' '.join([
            self.player, 'to', self.x, self.y
        ])
