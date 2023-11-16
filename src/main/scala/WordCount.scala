import com.spotify.scio._
import org.apache.beam.sdk.PipelineResult
object WordCount {
  def main(CmdArgs: Array[String]): Unit = {
    if (CmdArgs.length <= 0) {
      println("Hello, World!")
      return
    }
    val (sc, args) = ContextAndArgs(CmdArgs)
    println("Hello world! The code has started executing")
    sc.options.setTempLocation("gs://test-bucket-deepansh/tmp/")

    val input = args.getOrElse("input", "gs://test-bucket-deepansh/input.txt")
    // val input = "Tsample input for work"
    val output = args.getOrElse("output", "gs://test-bucket-deepansh/output")
    println(s"The input file is :- $input")
    println(s"The output folder is :- $output")

    sc.textFile(input)
      .flatMap(_.split("[^a-zA-Z']+").filter(_.nonEmpty))
      .countByValue
      .map(kv => kv._1 + ": " + kv._2)
      .saveAsTextFile(output)
    val res = sc.run().waitUntilFinish()
    // result.waitUntilFinish()
    if (res.state == PipelineResult.State.DONE)
      println(s"SUCCESS: Pipeline read and showed the word count")
    else {
      println(s"Pipeline failed:")
      throw new Exception("pipeline failed")
    }
  }
}