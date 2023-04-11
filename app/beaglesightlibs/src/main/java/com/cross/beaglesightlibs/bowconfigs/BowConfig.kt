package com.cross.beaglesightlibs.bowconfigs

import android.util.Log
import com.squareup.moshi.JsonAdapter
import com.squareup.moshi.JsonClass
import com.squareup.moshi.Moshi
import org.apache.commons.math3.linear.Array2DRowRealMatrix
import org.apache.commons.math3.linear.ArrayRealVector
import org.apache.commons.math3.linear.DecompositionSolver
import org.apache.commons.math3.linear.LUDecomposition
import org.apache.commons.math3.linear.RealMatrix
import org.apache.commons.math3.linear.RealVector
import java.io.FileOutputStream
import java.io.InputStream
import java.util.Objects
import java.util.UUID

@JsonClass(generateAdapter = true)
data class BowConfig(
    var id: String = UUID.randomUUID().toString(),
    var name: String = "",
    var description: String = "",
    var positionArray: List<PositionPair> = listOf(),
) {
    @Transient
    private var size = 0
    @Transient
    private var order = 4
    @Transient
    private var polynomial: RealVector? = null

    fun calcPosition(distance: Float): Float {
        if (polynomial == null) {
            calcPolynomial()
        }
        if (size < 2) {
            return Float.NaN
        }
        val `val` = DoubleArray(order)
        for (j in 0 until order) {
            `val`[j] = Math.pow(distance.toDouble(), (order - 1 - j).toDouble())
        }
        val a: RealVector = ArrayRealVector(`val`)
        return a.dotProduct(polynomial).toFloat()
    }

    /**
     * ideas from here: http://www.had2know.com/academics/quadratic-regression-calculator.html
     */
    private fun calcPolynomial() {
        try {
            size = positionArray.size
            if (size < 2) {
                return
            }
            order = size + 1
            if (order > 4) {
                order = 4
            }
            val values = Array(order) { DoubleArray(order) }
            val rhs = DoubleArray(order)
            val xsum = DoubleArray(2 * order - 1)
            for (i in 0 until order) {
                rhs[i] = sum(positionArray, order - 1 - i, 1).toDouble()
            }
            for (i in 0 until 2 * (order - 1)) {
                xsum[i] = sum(positionArray, i, 0).toDouble()
            }
            for (i in 0 until order) {
                for (j in 0 until order) {
                    values[i][j] = xsum[2 * (order - 1) - i - j]
                }
            }
            val a: RealMatrix = Array2DRowRealMatrix(values)

            //Log.e("BeagleSight","a matrix: " + a);
            val solver: DecompositionSolver = LUDecomposition(a).solver
            val b: RealVector = ArrayRealVector(rhs)
            polynomial = solver.solve(b)
            Log.i("BeagleSight", a.toString())
            Log.i("BeagleSight", b.toString())
            Log.i("BeagleSight", polynomial.toString())
        } catch (e: Exception) {
            Log.e("BeagleSight", e.message!!)
        }
    }

    private fun sum(positionArray: List<PositionPair>, xpower: Int, ypower: Int): Float {
        var v = 0f
        for (pair in positionArray) {
            val x = pair.distance
            val y = pair.position
            v += (Math.pow(x.toDouble(), xpower.toDouble())
                    * Math.pow(
                y.toDouble(), ypower.toDouble()
            )).toFloat()
        }
        return v
    }

    override fun toString(): String {
        return String.format("ID: %s, Name: %s, Desc: %s", id, name, description)
    }

    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (other !is BowConfig) return false
        return id == other.id && name == other.name && description == other.description && positionArray == other.positionArray
    }

    override fun hashCode(): Int {
        return Objects.hash(id, name, description, positionArray)
    }

    fun export(outputStream: FileOutputStream) {
        val moshi: Moshi = Moshi.Builder().build()
        val jsonAdapter: JsonAdapter<BowConfig> = moshi.adapter(BowConfig::class.java)
        outputStream.write(jsonAdapter.toJson(this).toByteArray())
        outputStream.close()
    }

    fun addPos(p: PositionPair) {
        val list = positionArray.toMutableList()
        list.add(p)
        positionArray = list.toList()
        calcPolynomial()
    }

    fun removePos(p: PositionPair) {
        val list = positionArray.toMutableList()
        list.remove(p)
        positionArray = list.toList()
        calcPolynomial()
    }

    companion object {
        fun load(inputStream: InputStream): BowConfig? {
            val moshi: Moshi = Moshi.Builder().build()
            val jsonAdapter: JsonAdapter<BowConfig> = moshi.adapter(BowConfig::class.java)

            try {
                val jsonData = String(inputStream.readBytes())

                return jsonAdapter.fromJson(jsonData)!!
            } catch (_: Exception) {
            }
            return null
        }
    }
}