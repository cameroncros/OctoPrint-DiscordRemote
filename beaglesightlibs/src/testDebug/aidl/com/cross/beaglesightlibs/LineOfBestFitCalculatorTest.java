package com.cross.beaglesightlibs;

import junit.framework.Assert;

import org.junit.jupiter.api.Test;

import java.util.HashMap;
import java.util.Map;


class LineOfBestFitCalculatorTest {

    @Test
    void calcPosition() {
        {
            Map<String, String> pos = new HashMap<>();
            pos.put("10", "10");
            LineOfBestFitCalculator calc = new LineOfBestFitCalculator();
            calc.setPositions(pos);
            Assert.assertEquals(Double.NaN, calc.calcPosition(11));
        }
        {
            Map<String, String> pos = new HashMap<>();
            pos.put("10", "10");
            pos.put("20", "20");
            LineOfBestFitCalculator calc = new LineOfBestFitCalculator();
            calc.setPositions(pos);
            Assert.assertEquals(15.0, calc.calcPosition(15));
        }
    }
}