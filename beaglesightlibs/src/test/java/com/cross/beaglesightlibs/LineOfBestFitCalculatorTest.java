package com.cross.beaglesightlibs;

import com.cross.beaglesightlibs.exceptions.InvalidNumberFormatException;

import org.junit.jupiter.api.Test;

import java.util.ArrayList;
import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;

class LineOfBestFitCalculatorTest {
    @Test
    void calcPosition() throws InvalidNumberFormatException {
        {
            List<PositionPair> pos = new ArrayList<>();
            pos.add(new PositionPair("10", "10"));
            LineOfBestFitCalculator calc = new LineOfBestFitCalculator();
            calc.setPositions(pos);
            assertEquals(Float.NaN, calc.calcPosition(11));
        }
        {
            List<PositionPair> pos = new ArrayList<>();
            pos.add(new PositionPair("10", "10"));
            pos.add(new PositionPair("20", "20"));
            LineOfBestFitCalculator calc = new LineOfBestFitCalculator();
            calc.setPositions(pos);
            assertEquals(15.0, calc.calcPosition(15));
        }
    }
}