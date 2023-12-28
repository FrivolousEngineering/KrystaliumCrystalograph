import random

from sql_app.schemas import Action


class MaskGenerator:
    def __init__(self):
        pass

    @staticmethod
    def getRandomMaskFunction():
        random_num = random.randint(1, 17)
        result = getattr(MaskGenerator, f"generateMask{random_num}")
        print("Generated mask ", random_num)
        return result

    @staticmethod
    def generateAngles(spacing, angle_width, start_angle=0, end_angle=360, shift=0):
        angle_to_add = start_angle + 0.5 * angle_width
        result = []
        while angle_to_add < end_angle + 0.5 * angle_width:
            result.append((angle_to_add, angle_width))
            angle_to_add += spacing
        return result

    @staticmethod
    def generateMask1(start_angle, end_angle):
        result = []
        result.extend(MaskGenerator.generateAngles(30, 10, start_angle, end_angle))
        result.extend(MaskGenerator.generateAngles(15, 5, start_angle, end_angle))
        result.extend(MaskGenerator.generateAngles(60, 20, start_angle, end_angle))
        return result

    @staticmethod
    def generateMask2(start_angle, end_angle):
        result = []
        result.extend(MaskGenerator.generateAngles(15, 5, start_angle, end_angle))
        result.extend(MaskGenerator.generateAngles(16, 10, start_angle, end_angle))
        return result

    @staticmethod
    def generateMask3(start_angle, end_angle):
        result = []
        result.extend(MaskGenerator.generateAngles(15, 5, start_angle, end_angle))
        result.extend(MaskGenerator.generateAngles(16, 5, start_angle, end_angle))
        return result

    @staticmethod
    def generateMask4(start_angle, end_angle):
        result = []
        result.extend(MaskGenerator.generateAngles(30, 5, start_angle, end_angle))
        result.extend(MaskGenerator.generateAngles(30, 5, start_angle, end_angle))
        result.extend(MaskGenerator.generateAngles(40, 5, start_angle, end_angle))
        result.extend(MaskGenerator.generateAngles(50, 5, start_angle, end_angle))
        return result

    @staticmethod
    def generateMask5(start_angle, end_angle):
        result = []
        result.extend(MaskGenerator.generateAngles(20, 10, start_angle, end_angle))
        result.extend(MaskGenerator.generateAngles(30, 15, start_angle, end_angle))
        return result

    @staticmethod
    def generateMask6(start_angle, end_angle):
        result = []
        result.extend(MaskGenerator.generateAngles(60, 10, start_angle, end_angle))
        result.extend(MaskGenerator.generateAngles(70, 10, start_angle, end_angle))
        return result

    @staticmethod
    def generateMask7(start_angle, end_angle):
        result = []
        result.extend(MaskGenerator.generateAngles(15, 2, start_angle, end_angle))
        result.extend(MaskGenerator.generateAngles(20, 3, start_angle, end_angle))
        return result

    @staticmethod
    def generateMask8(start_angle, end_angle):
        result = []
        result.extend(MaskGenerator.generateAngles(15, 2, start_angle, end_angle))
        result.extend(MaskGenerator.generateAngles(20, 3, start_angle, end_angle))
        result.extend(MaskGenerator.generateAngles(25, 3, start_angle, end_angle))
        return result

    @staticmethod
    def generateMask9(start_angle, end_angle):
        result = []
        result.extend(MaskGenerator.generateAngles(30, 10, start_angle + 10, end_angle))
        result.extend(MaskGenerator.generateAngles(60, 15, start_angle + 20, end_angle))
        result.extend(MaskGenerator.generateAngles(15, 2, start_angle + 10, end_angle))
        return result

    @staticmethod
    def generateMask10(start_angle, end_angle):
        result = []
        result.extend(MaskGenerator.generateAngles(10, 5, start_angle, start_angle + 60 + 5))
        result.extend(MaskGenerator.generateAngles(20, 10, start_angle + 60, end_angle - 60))
        result.extend(MaskGenerator.generateAngles(10, 5, end_angle - 60, end_angle))
        return result

    @staticmethod
    def generateMask11(start_angle, end_angle):
        result = []
        result.extend(MaskGenerator.generateAngles(20, 10, start_angle, start_angle + 60 + 5))
        result.extend(MaskGenerator.generateAngles(10, 5, start_angle + 60, end_angle - 60))
        result.extend(MaskGenerator.generateAngles(20, 10, end_angle - 60, end_angle))
        return result

    @staticmethod
    def generateMask12(start_angle, end_angle):
        result = []
        result.extend(MaskGenerator.generateAngles(15, 10, start_angle, start_angle + 60 + 5))
        result.extend(MaskGenerator.generateAngles(8, 5, start_angle + 60, end_angle - 60))
        result.extend(MaskGenerator.generateAngles(15, 10, end_angle - 60, end_angle))
        return result

    @staticmethod
    def generateMask13(start_angle, end_angle):
        result = []
        result.extend(MaskGenerator.generateAngles(8, 5, start_angle, start_angle + 60 + 5))
        result.extend(MaskGenerator.generateAngles(15, 10, start_angle + 60, end_angle - 60))
        result.extend(MaskGenerator.generateAngles(8, 5, end_angle - 60, end_angle))
        return result

    @staticmethod
    def generateMask14(start_angle, end_angle):
        result = []
        half_angle = abs(end_angle - start_angle) / 2
        result.extend(MaskGenerator.generateAngles(12, 6, start_angle, start_angle + half_angle))
        result.extend(MaskGenerator.generateAngles(22, 11, start_angle + half_angle, end_angle))
        return result

    @staticmethod
    def generateMask15(start_angle, end_angle):
        result = []
        half_angle = abs(end_angle - start_angle) / 2
        result.extend(MaskGenerator.generateAngles(22, 11, start_angle, start_angle + half_angle))
        result.extend(MaskGenerator.generateAngles(12, 6, start_angle + half_angle, end_angle))
        return result

    @staticmethod
    def generateMask16(start_angle, end_angle):
        result = []
        result.extend(MaskGenerator.generateAngles(4, 2, start_angle, end_angle))
        return result

    @staticmethod
    def generateMask17(start_angle, end_angle):
        result = []
        result.extend(MaskGenerator.generateAngles(8, 4, start_angle, end_angle))
        result.extend(MaskGenerator.generateAngles(4, 2, start_angle, end_angle))
        return result

    @staticmethod
    def getMaskFunctionByAction(action):
        action_list = list(Action)
        result = getattr(MaskGenerator, f"generateMask{action_list.index(action.title()) + 1}")
        return result