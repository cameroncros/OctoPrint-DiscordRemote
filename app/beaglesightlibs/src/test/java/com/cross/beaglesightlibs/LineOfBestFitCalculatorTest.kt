package com.cross.beaglesightlibs

import com.cross.beaglesightlibs.bowconfigs.LineOfBestFitCalculator
import com.cross.beaglesightlibs.bowconfigs.PositionPair
import com.cross.beaglesightlibs.exceptions.InvalidNumberFormatException
import org.junit.Assert
import org.junit.Test

class LineOfBestFitCalculatorTest {
    @Test
    @Throws(InvalidNumberFormatException::class)
    fun calcPosition() {
        run {
            val pos: MutableList<PositionPair> = ArrayList()
            pos.add(PositionPair(10.0f, 10.0f))
            val calc = LineOfBestFitCalculator()
            calc.positions = pos
            Assert.assertEquals(Double.NaN, calc.calcPosition(11.0f).toDouble(), 0.001)
        }
        run {
            val pos: MutableList<PositionPair> = ArrayList()
            pos.add(PositionPair(10.0f, 10.0f))
            pos.add(PositionPair(20.0f, 20.0f))
            val calc = LineOfBestFitCalculator()
            calc.positions = pos
            Assert.assertEquals(15.0f, calc.calcPosition(15.0f), 0.001f)
        }
    }
}