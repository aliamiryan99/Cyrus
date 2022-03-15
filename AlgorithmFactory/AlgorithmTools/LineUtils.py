
import numpy as np
import math


def rotate_line(x, y, deg):  # Vertices matrix
    v = np.array((x, y, np.zeros(y.size))).transpose()
    v_centre = np.mean(v, 0)  # Centre, of line
    vc = v - np.ones((v.shape[0], 1)) * v_centre  # Centering coordinates
    a_rad = ((deg * math.pi) / 180)  # Angle in radians

    e = np.array([0, 0, a_rad])  # Euler angles for X, Y, Z - axis rotations

    # Direction Cosines (rotation matrix) construction
    rx = np.array([[1, 0, 0],
                   [0, np.cos(e[0]), -np.sin(e[0])],
                   [0, np.sin(e[0]), np.cos(e[0])]])  # X-Axis rotation

    ry = np.array([[np.cos(e[1]), 0, np.sin(e[1])],
                   [0, 1, 0],
                   [-np.sin(e[1]), 0, np.cos(e[1])]])  # Y-axis rotation

    rz = np.array([[np.cos(e[2]), -np.sin(e[2]), 0],
                   [np.sin(e[2]), np.cos(e[2]), 0],
                   [0, 0, 1]])  # Z-axis rotation

    r = rx.dot(ry.dot(rz))  # Rotation matrix
    vrc = (r.dot(vc.transpose())).transpose()  # Rotating centred coordinates
    vr = vrc + np.ones((v.shape[0], 1)) * v_centre  # Shifting back to original location
    x = vr[:, 0]
    y = vr[:, 1]
    return x, y


def rotate_line2(x, y, deg):
    v = np.array((x, y, )).transpose()
    v_centre = np.mean(v, 0)  # Centre, of line
    vc = v - np.ones((v.shape[0], 1)) * v_centre  # Centering coordinates
    a_rad = ((deg * math.pi) / 180)  # Angle in radians

    e = np.array([0, 0, a_rad])  # Euler angles for X, Y, Z - axis rotations

    # Direction Cosines (rotation matrix) construction
    rx = np.array([[1, 0, 0],
                   [0, np.cos(e[0]), -np.sin(e[0])],
                   [0, np.sin(e[0]), np.cos(e[0])]])  # X-Axis rotation

    ry = np.array([[np.cos(e[1]), 0, np.sin(e[1])],
                   [0, 1, 0],
                   [-np.sin(e[1]), 0, np.cos(e[1])]])  # Y-axis rotation

    rz = np.array([[np.cos(e[2]), -np.sin(e[2]), 0],
                   [np.sin(e[2]), np.cos(e[2]), 0],
                   [0, 0, 1]])  # Z-axis rotation

    r = rx.dot(ry.dot(rz))  # Rotation matrix
    vrc = (r.dot(vc.transpose())).transpose()  # Rotating centred coordinates
    vr = vrc + np.ones((v.shape[0], 1)) * v_centre  # Shifting back to original location
    x = vr[:, 0]
    y = vr[:, 1]
    return x, y