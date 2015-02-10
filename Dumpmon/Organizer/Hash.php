<?php

namespace Dumpmon\Organizer;

class Hash extends Organizer
{
    public function analyze()
    {
        $hashes = $this->detectMd5();

        $this->score = $hashes / $this->lines;
    }

    protected function detectMd5()
    {
        return (int) preg_match_all('/[a-f0-9]{32}/i', $this->data);
    }

    protected function detectMd5Crypt()
    {
        // Example (unsalted) $1$sCGfZOwq$K9M3ULuacSQln/e3/KnPN.
    }

    protected function detectSha1()
    {
        // Regex \b[0-9a-f]{40}\b
    }

    protected function detectMySQL()
    {
        // Regex /\*[a-f0-9]{40}/i
    }
}