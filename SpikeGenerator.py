

import random

from sql_app.schemas import Target


class SpikeGenerator:
    def __init__(self):
        pass

    @staticmethod
    def generateSpikes1(start_angle, end_angle):
        half_angle = abs(end_angle - start_angle) / 2
        result = [(start_angle + half_angle, 40, 0.15),
                  (start_angle + half_angle, 30, -0.05),
                  (start_angle + half_angle, 15, -0.15),
                  (start_angle + half_angle, 2, 0.2)]
        return result

    @staticmethod
    def generateSpikes2(start_angle, end_angle):
        third_angle = abs(end_angle - start_angle) / 3
        result = [(start_angle + third_angle, 20, 0.05),
                  (end_angle - third_angle, 20, -0.05)]
        return result

    @staticmethod
    def generateSpikes3(start_angle, end_angle):
        third_angle = abs(end_angle - start_angle) / 3
        half_angle = abs(end_angle - start_angle) / 2
        result = [(start_angle + third_angle, 20, 0.05),
                  (start_angle + half_angle, 20, -0.05),
                  (end_angle - third_angle, 20, 0.05)]
        return result

    @staticmethod
    def generateSpikes4(start_angle, end_angle):
        quarter_angle = abs(end_angle - start_angle) / 4
        third_angle = abs(end_angle - start_angle) / 3
        result = [(start_angle + quarter_angle, 20, 0.1),
                  (start_angle + third_angle, 5, -0.1),
                  (end_angle - third_angle, 5, -0.1),
                  (end_angle - quarter_angle, 20, 0.1)]
        return result

    @staticmethod
    def generateSpikes5(start_angle, end_angle):
        quarter_angle = abs(end_angle - start_angle) / 4
        third_angle = abs(end_angle - start_angle) / 3
        result = [(start_angle + quarter_angle, 5, -0.1),
                  (start_angle + third_angle, 5, -0.1),
                  (end_angle - third_angle, 5, -0.1),
                  (end_angle - quarter_angle, 5, -0.1)]
        return result

    @staticmethod
    def generateSpikes6(start_angle, end_angle):
        quarter_angle = abs(end_angle - start_angle) / 4
        third_angle = abs(end_angle - start_angle) / 3
        half_angle = abs(end_angle - start_angle) / 2
        result = [(start_angle + quarter_angle, 10, -0.1),
                  (start_angle + third_angle, 10, -0.1),
                  (start_angle + half_angle, 10, -0.15),
                  (end_angle - third_angle, 10, -0.1),
                  (end_angle - quarter_angle, 10, -0.1)]
        return result

    @staticmethod
    def generateSpikes7(start_angle, end_angle):
        half_angle = abs(end_angle - start_angle) / 2
        result = [(start_angle + half_angle, half_angle, -0.15)]
        return result

    @staticmethod
    def generateSpikes8(start_angle, end_angle):
        half_angle = abs(end_angle - start_angle) / 2
        result = [(start_angle + half_angle, half_angle, 0.15)]
        return result

    @staticmethod
    def generateSpikes9(start_angle, end_angle):
        half_angle = abs(end_angle - start_angle) / 2
        quarter_angle = abs(end_angle - start_angle) / 4
        third_angle = abs(end_angle - start_angle) / 3
        result = [(start_angle + third_angle, quarter_angle, 0.05),
                  (start_angle + quarter_angle, 5, -0.1),
                  (start_angle + half_angle, third_angle, 0.15),
                  (start_angle + half_angle, 5, -0.15),
                  (end_angle - quarter_angle, 5, -0.1),
                  (end_angle - third_angle, quarter_angle, 0.05)]
        return result

    @staticmethod
    def generateSpikes10(start_angle, end_angle):
        half_angle = abs(end_angle - start_angle) / 2
        quarter_angle = abs(end_angle - start_angle) / 4

        result = [(start_angle + quarter_angle, 10, 0.15),
                  (start_angle + half_angle, 10, -0.15),
                  (end_angle - quarter_angle, 10, 0.15)]
        return result

    @staticmethod
    def getRandomSpikeFunction():
        target = random.choice(list(Target))
        print(f"Giving Spike for {target}")
        return SpikeGenerator.getSpikeFunctionByTarget(target)

    @staticmethod
    def getSpikeFunctionByTarget(target):
        target_list = list(Target)
        result = getattr(SpikeGenerator, f"generateSpikes{target_list.index(target.title()) + 1}")
        return result
