package com.cross.beaglesightlibs;

import com.cross.beaglesightlibs.exceptions.InvalidNumberFormatException;

import junit.framework.Assert;

import org.junit.jupiter.api.Test;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;


class LineOfBestFitCalculatorTest {

    @Test
    void calcPosition() throws InvalidNumberFormatException {
        {
            List<PositionPair> pos = new ArrayList<>();
            pos.add(new PositionPair("10", "10"));
            LineOfBestFitCalculator calc = new LineOfBestFitCalculator();
            calc.setPositions(pos);
            Assert.assertEquals(Double.NaN, calc.calcPosition(11));
        }
        {
            List<PositionPair> pos = new ArrayList<>();
            pos.add(new PositionPair("10", "10"));
            pos.add(new PositionPair("20", "20"));
            LineOfBestFitCalculator calc = new LineOfBestFitCalculator();
            calc.setPositions(pos);
            Assert.assertEquals(15.0, calc.calcPosition(15));
        }
    }
}