import copy

class Evaluator:
    def __init__(self, tasks):
        self.tasks = tasks

    def accuracy(self):
        """
        Compute the accuracy: Acc = number of correct answers / total number of tasks
        """
        correct = sum(1 for task in self.tasks if task.answer == task.correct_answer)
        return correct / len(self.tasks)

    def calculate_ranks(self, task):
        """
        For each correct_rule_id, compute its rank (position) in the predicted rule_id list.
        Returns a dictionary mapping each correct_rule_id to its rank.
        If a correct_rule_id is not found in the predicted list, its rank is set to None.
        """
        # Get predicted rule IDs
        predicted_rule_ids = task.get_rule_id()

        # Ensure correct_rule_id is a list
        correct_rule_ids = task.correct_rule_id
        if isinstance(correct_rule_ids, str):
            correct_rule_ids = [correct_rule_ids]
        elif isinstance(correct_rule_ids, (list, set)):
            correct_rule_ids = list(correct_rule_ids)
        else:
            correct_rule_ids = []

        # Create a dictionary to store ranks
        ranks = {}

        # For each correct_rule_id, find its rank
        for correct_rule_id in correct_rule_ids:
            try:
                # Rank is position + 1 (since positions start from 0)
                predicted_rule_ids_ = copy.deepcopy(predicted_rule_ids)
                correct_rule_ids_ = copy.deepcopy(correct_rule_ids)
                correct_rule_ids_.remove(correct_rule_id)
                for rm_cri in correct_rule_ids_:
                    predicted_rule_ids_.remove(rm_cri)
                rank = predicted_rule_ids_.index(correct_rule_id) + 1
            except ValueError:
                # If correct_rule_id is not in predicted_rule_ids
                rank = None
            ranks[correct_rule_id] = rank

        return ranks

    def hit_at_k(self, task, k):
        """
        Compute the Hit@K for a single task.
        For each correct_rule_id, check if it is within top K predicted rules.
        Returns the average Hit@K over all correct_rule_ids for the task.
        """
        ranks = self.calculate_ranks(task)
        hits = []

        for rank in ranks.values():
            if rank is not None and rank <= k:
                hits.append(1)
            else:
                hits.append(0)

        if hits:
            return sum(hits) / len(hits)
        else:
            return 0.0  # No correct_rule_ids to evaluate

    def hit_score(self):
        """
        Compute the overall Hit score:
        Hit = (3 * Hit@3 + 2 * Hit@5 + Hit@7 + Hit@10) / 7
        The Hit@K for each task is averaged over all correct_rule_ids.
        """
        total_hit = 0.0
        num_tasks = len(self.tasks)

        for task in self.tasks:
            hit3 = self.hit_at_k(task, 3)
            hit5 = self.hit_at_k(task, 5)
            hit7 = self.hit_at_k(task, 7)
            hit10 = self.hit_at_k(task, 10)

            task_hit = (3 * hit3 + 2 * hit5 + hit7 + hit10) / 7
            total_hit += task_hit

        return total_hit / num_tasks

    def final_score(self):
        """
        Compute the final score: Final_score = (Acc + Hit) / 2
        """
        acc = self.accuracy()
        hit = self.hit_score()
        return (acc + hit) / 2
