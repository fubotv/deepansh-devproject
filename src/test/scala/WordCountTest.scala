import cats.implicits.catsSyntaxEq

class HelloSpec extends munit.FunSuite {
//  test("say hello") {
//    val stringArray: Array[String] = Array("Hello", "World", "Scala")
//    assertEquals(WordCount.main(stringArray), "hello")
//  }
  test("Main.main should print 'Hello, World!' when no arguments are provided") {
    val output = new java.io.ByteArrayOutputStream()
    Console.withOut(output) {
      WordCount.main(Array.empty[String])
    }
    println(output)
    assert(output.toString.trim === "Hello, World!")

  }
}