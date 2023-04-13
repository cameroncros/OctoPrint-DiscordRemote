package com.cross.beaglesightlibs

import com.cross.beaglesightlibs.bowconfigs.BowConfig
import com.cross.beaglesightlibs.bowconfigs.PositionPair
import com.cross.beaglesightlibs.exceptions.InvalidNumberFormatException
import junit.framework.Assert.assertEquals
import org.junit.Assert
import org.junit.Test
import java.io.File
import java.io.FileInputStream
import java.io.FileOutputStream

class BowConfigTest {
    @Test
    fun exportAndImport() {
        val bc = BowConfig()
        val fos = FileOutputStream(File("bc.json"))
        bc.export(fos)

        val fis = FileInputStream(File("bc.json"))
        val bc2 = BowConfig.load(fis)
        assertEquals(bc, bc2)

        File("bc.json").delete()
    }

    @Test
    @Throws(InvalidNumberFormatException::class)
    fun calcPosition() {
        run {
            val pos: MutableList<PositionPair> = ArrayList()
            pos.add(PositionPair(10.0f, 10.0f))
            val calc = BowConfig("", "", "", pos)
            Assert.assertEquals(Double.NaN, calc.calcPosition(11.0f).toDouble(), 0.001)
        }
        run {
            val pos: MutableList<PositionPair> = ArrayList()
            pos.add(PositionPair(10.0f, 10.0f))
            pos.add(PositionPair(20.0f, 20.0f))
            val calc = BowConfig("", "", "", pos)
            Assert.assertEquals(15.0f, calc.calcPosition(15.0f), 0.001f)
        }
    }
}