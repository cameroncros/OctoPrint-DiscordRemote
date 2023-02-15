package com.cross.beaglesightlibs.bowconfigs

import android.util.Log
import org.apache.commons.math3.linear.Array2DRowRealMatrix
import org.apache.commons.math3.linear.ArrayRealVector
import org.apache.commons.math3.linear.DecompositionSolver
import org.apache.commons.math3.linear.LUDecomposition
import org.apache.commons.math3.linear.RealMatrix
import org.apache.commons.math3.linear.RealVector

class LineOfBestFitCalculator : PositionCalculator() {
    private var size = 0
    private var order = 4
    private var polynomial: RealVector? = null

    override fun calcPosition(distance: Float): Float {
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
            size = positions!!.size
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
                rhs[i] = sum(positions!!, order - 1 - i, 1).toDouble()
            }
            for (i in 0 until 2 * (order - 1)) {
                xsum[i] = sum(positions!!, i, 0).toDouble()
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
        var `val` = 0f
        for (pair in positionArray) {
            val x = pair.distance
            val y = pair.position
            `val` += (Math.pow(x.toDouble(), xpower.toDouble())
                    * Math.pow(
                y.toDouble(), ypower.toDouble()
            )).toFloat()
        }
        return `val`
    }
}