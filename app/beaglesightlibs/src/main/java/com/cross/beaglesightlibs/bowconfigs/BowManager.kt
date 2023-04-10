package com.cross.beaglesightlibs.bowconfigs

import android.content.Context
import com.squareup.moshi.JsonAdapter
import com.squareup.moshi.Moshi
import java.io.File
import java.io.FileInputStream
import java.io.FileOutputStream

private const val PREFIX: String = "bowconfig_"

fun listFiles(filesDir: File) = iterator {
    val dir = filesDir.listFiles() ?: return@iterator
    for (file in dir) {
        if (file.isDirectory) {
            continue
        }
        if (!file.name.startsWith(PREFIX)) {
            continue
        }
        yield(file)
    }
}

class BowManager(context: Context) {
    private var filesDir: File
    private val configs: HashMap<String, BowConfig>

    init {
        filesDir = context.filesDir
        configs = HashMap()
        loadAll()
    }

    private fun generateFilename(filesDir: File, filename: String): File {
        return File(
            filesDir.canonicalPath + File.separator + PREFIX + filename + ".json"
        )
    }

    fun allBowConfigs(): List<BowConfig> {
        return configs.values.toMutableList()
    }

    fun deleteBowConfig(bowConfig: BowConfig) {
        configs.remove(bowConfig.id)
        delete(bowConfig)
    }

    fun addBowConfig(bowConfig: BowConfig) {
        configs[bowConfig.id] = bowConfig
        persist(bowConfig)
    }

    fun getBowConfig(id: String): BowConfig? {
        return configs[id]
    }

    private fun loadAll() {
        val moshi: Moshi = Moshi.Builder().build()
        val jsonAdapter: JsonAdapter<BowConfig> = moshi.adapter(BowConfig::class.java)

        for (file in listFiles(filesDir)) {
            try {
                val inputString = FileInputStream(file)
                val jsonData = String(inputString.readBytes())

                val bowConfig: BowConfig = jsonAdapter.fromJson(jsonData)!!
                configs[bowConfig.id] = bowConfig
            } catch (_: Exception) {
            }
        }
    }

    fun persist(config: BowConfig) {
        val moshi: Moshi = Moshi.Builder().build()
        val jsonAdapter: JsonAdapter<BowConfig> = moshi.adapter(BowConfig::class.java)

        val json: String = jsonAdapter.toJson(config)
        val file = generateFilename(filesDir, config.id)

        val outputStream = FileOutputStream(file)
        outputStream.write(json.toByteArray())
        outputStream.close()
    }

    fun delete(config: BowConfig) {
        val file = generateFilename(filesDir, config.id)
        file.delete()
    }

    companion object {
        private var instance: BowManager? = null
        fun getInstance(cont: Context?): BowManager? {
            synchronized(BowManager::class.java) {
                if (instance == null && cont != null) {
                    instance = BowManager(cont)
                }
            }
            return instance
        }
    }
}