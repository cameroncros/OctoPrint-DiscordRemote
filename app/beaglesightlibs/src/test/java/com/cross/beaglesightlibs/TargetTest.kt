package com.cross.beaglesightlibs

import com.cross.beaglesightlibs.map.XmlParser
import org.junit.Assert
import org.junit.Test
import org.xml.sax.SAXException
import java.io.File
import java.io.FileInputStream
import java.io.IOException
import javax.xml.parsers.ParserConfigurationException

class TargetTest {
    @Test
    @Throws(ParserConfigurationException::class, SAXException::class, IOException::class)
    fun PublishedTargetsXML() {
        val targetFile = File("../../default_configs/targets.xml")
        val fis = FileInputStream(targetFile)
        val targets = XmlParser.parseTargetsXML(fis)
        Assert.assertNotEquals(0, targets.size.toLong())
    }
}