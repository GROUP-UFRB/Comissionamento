class ComputeCommission:
    def __init__(self):
        self.__commissions = {
            "RM": {"continuous": 0.03, "sporadic": 0.06, "high_cost": 0.08},
            "RD": {"continuous": 0.04, "sporadic": 0.07, "high_cost": 0.09},
            "RP1": {"continuous": 0.20, "sporadic": 0.30, "high_cost": 0.40},
            "RP2": {"continuous": 0.25, "sporadic": 0.35, "high_cost": 0.50},
            "RP3": {"continuous": 0.34, "sporadic": 0.47, "high_cost": 0.69},
            "RG": {"continuous": 0.05, "sporadic": 0.08, "high_cost": 0.10},
            "RC": {"continuous": 0.10, "sporadic": 0.12, "high_cost": 0.20},
            "RV": {"continuous": 0.15, "sporadic": 0.20, "high_cost": 0.30},
        }
        self.__default_roles = [
            ["RV", "RC", "RG", "RD", "RM"],
            ["RP1", "RM"],
            ["RP2", "RM"],
            ["RP3", "RM"],
        ]
        self.__hierarchy = []
        self.__labels = []
        self.__roles = []

    def __create_hierarchy(self, result):
        for record in result:
            path = record["path"]
            for node in path.nodes:
                label = list(node.labels)[0]
                self.__hierarchy.append({"name": node["name"], "position": label})
                self.__labels.append(label)

    def __find_index(self):
        for i, row in enumerate(self.__default_roles):
            if self.__labels[0] in row:
                return i

    def __create_dict_commissions(self, commission):
        commissions_values = {}
        for label in self.__labels:
            if label in commissions_values:
                self.__hierarchy.pop(0)
                aux = commissions_values[label]

                commissions_values[label] = []
                commissions_values[label].append(aux)
                commissions_values[label].append(
                    {
                        "name": [
                            item["name"]
                            for item in self.__hierarchy
                            if item["position"] == label
                        ][0],
                        "commission": 0.0,
                    }
                )
            else:
                while True:
                    role = self.__roles.pop(0)
                    if label not in commissions_values:
                        commissions_values[label] = {
                            "name": [
                                item["name"]
                                for item in self.__hierarchy
                                if item["position"] == label
                            ][0],
                            "commission": 0.0,
                        }

                    commissions_values[label]["commission"] += (
                        self.__commissions[role][commission.type_commission]
                        * commission.value
                    )
                    if role == label:
                        break
        return commissions_values

    @classmethod
    def compute_commission(cls, result, commission):
        instance = cls()
        instance.__create_hierarchy(result)
        instance.__roles = instance.__default_roles[instance.__find_index()]
        return instance.__create_dict_commissions(commission)
