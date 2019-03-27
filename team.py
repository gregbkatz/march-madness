class Team:
    def __init__(self, data):
        self.playin_flag = data['playin_flag']
        self.id = int(data['team_id'])
        self.name = data['team_name']
        self.rating = data['team_rating']
        self.region = data['team_region']
        self.seed = data['team_seed']
        self.final_round = -1

    def print(self):
        return '{:5} {:8} {:12}'.format(
            self.seed, self.region, self.name[0:12])

    def write_to_truth_file(self, fo):
        fo.write('{},{}\n'.format(self.name, self.final_round))

    def update_final_round(self, final_round):
        self.final_round = final_round