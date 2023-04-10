package com.cross.beaglesightlibs

import com.cross.beaglesightlibs.bowconfigs.BowConfig
import junit.framework.Assert.assertEquals
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
}