<?php

namespace Dumpmon\Detector;

class Hash extends Detector
{
    private $functions;

    public function __construct()
    {
        $this->functions = array(
            'fewLines'       => 1,
            'longLines'      => 1,
            'detectMd5'      => 1,
            'detectMd5Crypt' => 1,
            'phpassMd5'      => 1,
            'phpassGen'      => 1,
            'detectSha1'     => 1,
            'detectMySQL'    => 1,
            'detectCrypt'    => 1,
            'detectDrupal'   => 1,
        );
    }

    public function analyze($results)
    {
        // If the Trash Detector has an high value, don't process the file, otherwise we could end up with a false positive
        // Sadly debug files LOVE to use hashes...
        if($results['trash'] >= 1)
        {
            $this->score = 0;

            return;
        }

        foreach($this->functions as $method => $coefficient)
        {
            if(method_exists($this, $method))
            {
                $score = $this->$method() * $coefficient;

                // Did I get a negative score? This means that this file is NOT an hash one!
                // Set the global score to 0 and stop here
                if($score < 0)
                {
                    $this->score = 0;
                    break;
                }

                $this->score += $score;
            }

            // I already reached the maximum value, there's no point in continuing
            if($this->score >= 3)
            {
                break;
            }
        }
    }

    protected function detectMd5()
    {
        $hashes = (int) preg_match_all('/[a-f0-9]{32}/im', $this->data);

        return $hashes / $this->lines;
    }

    protected function detectMd5Crypt()
    {
        // Example (unsalted) $1$sCGfZOwq$K9M3ULuacSQln/e3/KnPN.
        $hashes = preg_match_all('/\$1\$.{8}\$.{22}/im', $this->data);

        return $hashes / $this->lines;
    }

    protected function phpassMd5()
    {
        // Example $H$9V1cX/WqUhsSWM0ipyB7HwFQqTQKxP1
        $hashes = preg_match_all('/\$H\$9.{30}/m', $this->data);

        return $hashes / $this->lines;
    }

    protected function phpassGen()
    {
        // Example $P$B52zg0z/Y5e96IpD4KJ7a9ByqcrKb01
        $hashes = preg_match_all('/\$P\$.{31}/m', $this->data);

        return $hashes / $this->lines;
    }

    protected function detectSha1()
    {
        // Regex \b[0-9a-f]{40}\b
        $hashes = preg_match_all('/\b[0-9a-f]{40}\b/im', $this->data);

        return $hashes / $this->lines;
    }

    protected function detectMySQL()
    {
        // Regex /\*[a-f0-9]{40}/i
        $hashes = preg_match_all('/\*[a-f0-9]{40}/im', $this->data);

        return $hashes / $this->lines;
    }

    protected function detectCrypt()
    {
        $hashes = preg_match_all('/[a-zA-Z0-9\/\.]{13}[,\s\n]/m', $this->data);

        return $hashes / $this->lines;
    }

    protected function detectDrupal()
    {
        // Drupal $S$DugG4yZmhfIGhNJJZMzKzh4MzOCkpsPBR9HtDIvqQeIyqLM6wyuM
        $hashes =  preg_match_all('/\$S\$.{52}/m', $this->data);

        return $hashes / $this->lines;
    }

    /**
     * Files with huge lines are debug info
     *
     * @return int
     */
    protected function longLines()
    {
        $lines = explode("\n", $this->data);

        foreach($lines as $line)
        {
            if(strlen($line) > 1000)
            {
                return -1;
            }
        }

        return 0;
    }

    protected function fewLines()
    {
        // If I just have few lines, most likely it's trash. I have to do this since sometimes some debug output are
        // crammed into a single line, screwing up all the stats
        if($this->lines < 3)
        {
            return -1;
        }

        return 0;
    }
}