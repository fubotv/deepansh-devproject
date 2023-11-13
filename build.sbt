
import Dependencies._
import sbt.Keys._
import sbt.{util, _}

// resolvers += Resolver.githubPackages("fubotv", "de-common")
resolvers += "Confluent" at "https://packages.confluent.io/maven/"
ThisBuild / evictionErrorLevel := Level.Warn

lazy val commonSettings = Defaults.coreDefaultSettings ++ Seq(
  organization := "com.example",
  version := "0.1.0-SNAPSHOT",
  scalaVersion := "2.13.8",
  scalacOptions ++= Seq(
    "-target:jvm-1.8",
    "-deprecation",
    "-feature",
    "-unchecked",
    "-Ymacro-annotations"
  ),
  javacOptions ++= Seq("-source", "1.8", "-target", "1.8")
)

lazy val macroSettings = Def.settings(
  libraryDependencies += "org.scala-lang" % "scala-reflect" % scalaVersion.value,
  libraryDependencies += "org.scalameta" %% "munit" % "0.7.29" % Test,
  libraryDependencies ++= {
    VersionNumber(scalaVersion.value) match {
      case v if v.matchesSemVer(SemanticSelector("2.12.x")) =>
        Seq(
          compilerPlugin(
            ("org.scalamacros" % "paradise" % scalaMacrosVersion).cross(CrossVersion.full)
          )
        )
      case _ => Nil
    }
  },
  // see MacroSettings.scala
  scalacOptions += "-Xmacro-settings:cache-implicit-schemas=true"
)

lazy val root: Project = (project in file("."))
  .settings(commonSettings)
  .settings(macroSettings)
  .settings(
    name := projectName,
    description := projectName,
    publish / skip := true,
    libraryDependencies ++= Seq(
      "com.spotify" %% "scio-core" % scioVersion,
      "com.spotify" %% "scio-extra" % scioVersion,
      "org.apache.beam" % "beam-runners-google-cloud-dataflow-java" % beamVersion
    )
  )
  .enablePlugins(PackPlugin)

// See https://www.scala-sbt.org/1.x/docs/Using-Sonatype.html for instructions on how to publish to Sonatype.

val scioVersion = "0.13.3"
val beamVersion = "2.50.0"
val projectName = "deepansh-devproject"
val scalaMacrosVersion = "2.1.1"

enablePlugins(sbtdocker.DockerPlugin, JavaAppPackaging, GitVersioning)

Universal / javaOptions ++= Seq(
  // -J params will be added as jvm parameters
  // "-J-Xmx64m",
  // "-J-Xms64m",
  // others will be added as app parameters
  // you can access any build setting/task here
  //s"-version=${version.value}"
)

git.formattedShaVersion := git.gitHeadCommit.value map { sha =>
  s"$sha".substring(0, 10)
}

docker / buildOptions := BuildOptions(cache = false)

dockerExposedPorts ++= Seq(9000, 9001)
dockerExposedUdpPorts += 4444
Docker / packageName := projectName
dockerAlias := DockerAlias(
  None,
  dockerUsername.value,
  (Docker / packageName).value,
  Some(git.formattedShaVersion.value.getOrElse("latest"))
)