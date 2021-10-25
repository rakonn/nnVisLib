import numpy as np
import sys
import random

import pygame as pg
from pygame import error, gfxdraw
from pygame.locals import *


DARK_MODE_COLOUR = (29, 29, 29)

# draw "collapsed" icons


class ModelDiagram():
    def __init__(self, surface, topLeftX, topLeftY, width, height, weights, fill=False, nodeRadius=10) -> None:
        """Mode can be "outline" or "fill" """
        self.topLeftX = topLeftX
        self.topLeftY = topLeftY
        self.width = width
        self.height = height
        self.weights = weights
        self.surface = surface
        self.fill = fill
        self.nodeRadius = nodeRadius
        self.nodeCounts = []
        self.collapsedIconCoords = []

        # precompute node coords
        self.coords = self.getNodeCoords()

    def getNodeCoords(self):
        nodeCoords = []
        # get first layer coords "input coords"
        nodeCoords.append(self.getLayerCoords(np.shape(self.weights[0])[1], 0))

        # get coords of every layer after
        for i in range(len(self.weights)):
            numNodes = np.shape(self.weights[i])[0]
            nodeCoords.append(self.getLayerCoords(numNodes, i+1))

        return nodeCoords

    def getLayerCoords(self, numNodes, layer: int):
        # safe layer dimensions in self.node counts for further reference
        self.nodeCounts.append(numNodes)

        layerCoords = []
        numLayers = len(self.weights) + 1
        yOffset = self.height / numNodes
        xOffset = self.width / numLayers
        collapsed = False

        # change node spacing and count when to many nodes are present
        if yOffset < (2 * self.nodeRadius):
            numNodes, yOffset = self.determineUnevenNodeData()
            collapsed = True

        # determine node coords
        for i in range(numNodes):
            yCoord = round(yOffset * (i + 1) - yOffset / 2)
            xCoord = round(xOffset * (layer + 1) - xOffset / 2)
            layerCoords.append((xCoord, yCoord))

        # delete "collapsed" icon coords from node list and put it in own list for these
        if collapsed:
            self.collapsedIconCoords.append(
                layerCoords.pop(int((numNodes - 1) / 2)))

        return layerCoords

    def determineUnevenNodeData(self):
        """Returns a uneven fitting number of nodes from each side of the Layer (top, bottom)"""
        # 3*node radius represents the minimum allowable distance between nodes
        numNodes = int(self.height / (self.nodeRadius * 3))
        if (numNodes % 2) == 0:
            numNodes -= 1

        yOffset = self.height / numNodes

        return numNodes, yOffset

    def drawNodes(self, colour=(255, 255, 255), fill=False):
        for layer in self.coords:
            for node in layer:
                # pg.draw.circle(self.surface, (255, 255, 255),
                #                (xCoord, yCoord), self.nodeRadius)
                gfxdraw.aacircle(self.surface, node[0], node[1],
                                 self.nodeRadius, colour)
                if fill:
                    gfxdraw.filled_circle(self.surface, node[0], node[1],
                                          self.nodeRadius, colour)

    def drawFullLayerConnections(self, layerNum):
        # for nodeIndex in range(len(self.coords[layerNum])):
        #     for targetIndex in range(len(self.coords[layerNum + 1])):
        #         pg.draw.aaline(self.surface, self.getWeightColour(self.getConnectionWeight(
        #             layerNum, nodeIndex, targetIndex)), self.coords[layerNum][nodeIndex], self.coords[layerNum + 1][targetIndex])
        self.drawCoordRangeConnections(layerNum, range(
            len(self.coords[layerNum])), range(len(self.coords[layerNum + 1])))

    def drawCoordRangeConnections(self, layerNum, nodeRange, targetNodeRange):
        for nodeIndex in nodeRange:
            for targetIndex in targetNodeRange:
                # weight colour needs to be determined
                pg.draw.aaline(self.surface, self.getWeightColour(self.getConnectionWeight(
                    layerNum, nodeIndex, targetIndex)), self.coords[layerNum][nodeIndex], self.coords[layerNum + 1][targetIndex])

    # collapsed symbol
    def drawCollapsedLayerConnections(self, layerNum):
        numLayerNodes = len(self.coords[layerNum])
        numNodes = int((numLayerNodes - 1) / 2)

        # draw first few coords before separation
        self.drawCoordRangeConnections(layerNum, range(
            0, numNodes+1), range(len(self.coords[layerNum + 1])))

        # insert collapsed symnol drawing HERE

        self.drawCoordRangeConnections(layerNum, range(
            numLayerNodes - numNodes - 1, numLayerNodes), range(len(self.coords[layerNum + 1])))

    def getConnectionWeight(self, startLayer, startNode, endNode):
        return self.weights[startLayer][endNode][startNode]

    def drawConnections(self):
        for layerNum in range(len(self.coords) - 1):
            # if nodes are collapsed draw in collapsed mode
            if len(self.coords[layerNum]) < self.nodeCounts[layerNum]:
                self.drawCollapsedLayerConnections(layerNum)
            else:
                self.drawFullLayerConnections(layerNum)

    # (performance) only do this when weights got updated and store in seperate colour matrix(list?, array?)
    def getWeightColour(self, weight):
        default = (30, 109, 235)
        colour = ()

        if weight >= 0:
            interpolation = 210 + (42 - 210) * weight
            if interpolation > 210:
                interpolation = 210
            elif interpolation < 42:
                interpolation = 42

            colour = (interpolation, interpolation, 210)
        else:
            interpolation = 42 + (210 - 42) * weight
            if interpolation > 210:
                interpolation = 210
            elif interpolation < 42:
                interpolation = 42

            colour = (210, interpolation, interpolation)

        return colour

    def draw(self):
        self.drawConnections()
        self.drawNodes(DARK_MODE_COLOUR, True)
        self.drawNodes()

    def weights(self, weights):
        if len(weights) != len(self.weights):
            raise ValueError
        self.weights = weights


def main():
    pg.init()

    WINDOW_HEIGHT = 500
    WINDOW_WIDTH = 500

    fps = 60
    fpsClock = pg.time.Clock()

    screen = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

    diagram = ModelDiagram(screen, 0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, [(np.random.rand(
        40, 50) - 0.5) * 2, (np.random.rand(5, 40) - 0.5) * 2, (np.random.rand(1, 10) - 0.5) * 2])

    while True:
        screen.fill(DARK_MODE_COLOUR)

        for event in pg.event.get():
            if event.type == QUIT:
                pg.quit()
                sys.exit()

        diagram.draw()

        pg.display.flip()
        fpsClock.tick(fps)


if __name__ == "__main__":
    main()
